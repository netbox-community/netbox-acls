from django import forms
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site, VirtualChassis
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ...constants import (
    ACL_ASSIGNMENT_MODELS,
    ACL_ASSIGNMENT_OBJECT_LOOKUPS,
    ACL_ASSIGNMENT_OBJECT_PARENT_LOOKUPS,
)
from ...forms import (
    ACLAssignmentBulkEditForm,
    ACLAssignmentFilterForm,
    ACLAssignmentForm,
    ACLAssignmentImportForm,
)
from ...models import AccessList, ACLAssignment
from .base import BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin

UNRESOLVABLE_CONTENT_TYPE_ID = 99999999


class ACLAssignmentFormTestCase(BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin, TestCase):
    """Form tests for ACLAssignment forms."""

    bulk_edit_form = ACLAssignmentBulkEditForm
    filter_form = ACLAssignmentFilterForm

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Device Type 1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")
        cls.device = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=device_type,
            role=device_role,
        )
        cls.interface = cls.device.interfaces.create(
            name="DeviceInterface1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        cluster_type = ClusterType.objects.create(name="Cluster Type 1", slug="cluster-type-1")
        cluster = Cluster.objects.create(name="Cluster 1", type=cluster_type)
        virtual_machine = VirtualMachine.objects.create(name="VM 1", cluster=cluster)
        cls.vminterface = virtual_machine.interfaces.create(name="eth0")

        cls.access_list = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

    def _bound_form(self, model, obj, direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS):
        """Bind the form, so the posted type reaches __init__."""
        return ACLAssignmentForm(
            data={
                "access_list": self.access_list.pk,
                "assigned_object_content_type": ContentType.objects.get_for_model(model).pk,
                "assigned_object_object_id": obj.pk,
                "direction": direction,
            },
        )

    def test_direction_defaults_to_none_on_an_add_form(self):
        """ObjectEditView passes an unsaved instance on add, not None, so cover that shape."""
        for kwargs in ({}, {"instance": ACLAssignment()}):
            with self.subTest(instance="unsaved" if kwargs else "absent"):
                form = ACLAssignmentForm(**kwargs)
                self.assertEqual(
                    form.initial["direction"],
                    ACLAssignmentDirectionChoices.DIRECTION_NONE,
                )

    def test_edit_form_keeps_the_stored_direction(self):
        """Seeding the default must not overwrite a saved value."""
        assignment = ACLAssignment.objects.create(
            access_list=self.access_list,
            assigned_object=self.interface,
            direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
        )
        form = ACLAssignmentForm(instance=assignment)
        self.assertEqual(
            form.initial["direction"],
            ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
        )

    def test_assigned_object_queryset_follows_type(self):
        """Test that the object picker's queryset is resolved from the posted content type."""
        form = self._bound_form(Interface, self.interface)
        field = form.fields["assigned_object"]
        self.assertIs(field.selected_model, Interface)
        self.assertEqual(field.queryset.model, Interface)
        self.assertNotIn("disabled", field.object_field.widget.attrs)

    def test_direction_enabled_for_interface_types(self):
        """Test that the direction is enabled and required for both interface types."""
        for model, obj in ((Interface, self.interface), (VMInterface, self.vminterface)):
            with self.subTest(model=model._meta.label_lower):
                form = self._bound_form(model, obj)
                self.assertFalse(form.fields["direction"].disabled)
                self.assertTrue(form.fields["direction"].required)

    def test_direction_disabled_for_host_types(self):
        """Test that the direction is disabled for host assignments."""
        form = self._bound_form(
            Device,
            self.device,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )
        self.assertTrue(form.fields["direction"].disabled)

    def test_assigned_object_type_choices_limited(self):
        """Test that the assignment type picker offers only the assignable models."""
        form = ACLAssignmentForm()
        self.assertQuerySetEqual(
            form.fields["assigned_object"].content_type_field.queryset.order_by("pk"),
            ContentType.objects.filter(ACL_ASSIGNMENT_MODELS).order_by("pk"),
            transform=lambda ct: ct,
        )

    def test_filterform_assigned_object_type_choices_limited(self):
        """Test that the filter form's type picker offers only the assignable models."""
        form = ACLAssignmentFilterForm()
        self.assertQuerySetEqual(
            form.fields["assigned_object_type_id"].queryset.order_by("pk"),
            ContentType.objects.filter(ACL_ASSIGNMENT_MODELS).order_by("pk"),
            transform=lambda ct: ct,
        )

    def test_filterform_assigned_object_type_cleans_to_content_types(self):
        """Test that the filter form's type picker resolves primary keys, not natural keys."""
        interface_type = ContentType.objects.get_for_model(Interface)
        vminterface_type = ContentType.objects.get_for_model(VMInterface)
        form = ACLAssignmentFilterForm(
            data={"assigned_object_type_id": [interface_type.pk, vminterface_type.pk]},
        )
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        self.assertCountEqual(
            form.cleaned_data["assigned_object_type_id"],
            [interface_type, vminterface_type],
        )

    def test_unresolvable_content_type_is_survivable(self):
        """
        Test that a content type id which no longer resolves leaves the form usable.

        The id is constrained to the field's own content type queryset, so an
        out-of-set value resolves to no model and the object picker stays disabled.
        """
        form = ACLAssignmentForm(initial={"assigned_object_content_type": UNRESOLVABLE_CONTENT_TYPE_ID})
        field = form.fields["assigned_object"]
        self.assertIsNone(field.selected_model)
        self.assertEqual(field.object_field.widget.attrs.get("disabled"), "disabled")

    def test_clean_assigns_object(self):
        """Test that a valid form assigns the selected object to the instance."""
        form = self._bound_form(Interface, self.interface)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        self.assertEqual(form.instance.assigned_object, self.interface)

    def test_bulkedit_assigned_object_queryset_follows_type(self):
        """Test that the bulk-edit object picker's queryset is resolved from the posted type."""
        form = ACLAssignmentBulkEditForm(
            data={"assigned_object_content_type": ContentType.objects.get_for_model(Interface).pk},
        )
        self.assertIs(form.fields["assigned_object"].selected_model, Interface)
        self.assertEqual(form.fields["assigned_object"].queryset.model, Interface)

    def test_bulkedit_direction_enabled_with_no_type_chosen(self):
        """A bulk edit with no type picked must still be able to change direction alone."""
        form = ACLAssignmentBulkEditForm(data={})
        self.assertIsNone(form.fields["assigned_object"].selected_model)
        self.assertFalse(form.fields["direction"].disabled)

    def test_bulkedit_direction_disabled_for_host_types(self):
        """Test that the bulk-edit direction is disabled for host assignments."""
        form = ACLAssignmentBulkEditForm(
            data={"assigned_object_content_type": ContentType.objects.get_for_model(Device).pk},
        )
        self.assertIs(form.fields["assigned_object"].selected_model, Device)
        self.assertTrue(form.fields["direction"].disabled)

    def test_choice_filters_accept_multiple_values(self):
        """The filter form's choice fields must be multi-selects, matching the filter set."""
        form = ACLAssignmentFilterForm()
        for field_name in ("family", "direction"):
            with self.subTest(field_name=field_name):
                self.assertIsInstance(form.fields[field_name], forms.MultipleChoiceField)


class ACLAssignmentObjectLookupTestCase(TestCase):
    """Guard the import lookup map against the content type filter drifting away from it."""

    def test_lookup_map_covers_every_assignable_type(self):
        """Test that the map names exactly the types the content type filter selects."""
        selected = {
            f"{object_type.app_label}.{object_type.model}"
            for object_type in ContentType.objects.filter(ACL_ASSIGNMENT_MODELS)
        }

        self.assertEqual(selected, set(ACL_ASSIGNMENT_OBJECT_LOOKUPS))

    def test_parent_lookups_are_a_subset_of_the_assignable_types(self):
        """Test that no parent qualifier names a type the assignment map does not carry."""
        self.assertLessEqual(set(ACL_ASSIGNMENT_OBJECT_PARENT_LOOKUPS), set(ACL_ASSIGNMENT_OBJECT_LOOKUPS))


class ACLAssignmentImportFormTestCase(TestCase):
    """Import form tests for ACLAssignment."""

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Device Type 1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")
        cls.device1 = Device.objects.create(name="Device 1", site=site, device_type=device_type, role=device_role)
        cls.device2 = Device.objects.create(name="Device 2", site=site, device_type=device_type, role=device_role)

        # The same interface name on two devices is what the parent column disambiguates.
        cls.interface1 = cls.device1.interfaces.create(name="Gi0/1", type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        cls.interface2 = cls.device2.interfaces.create(name="Gi0/1", type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        cls.spare = cls.device1.interfaces.create(name="Gi0/2", type=InterfaceTypeChoices.TYPE_1GE_FIXED)

        cluster_type = ClusterType.objects.create(name="Cluster Type 1", slug="cluster-type-1")
        cluster = Cluster.objects.create(name="Cluster 1", type=cluster_type)
        cls.virtual_machine = VirtualMachine.objects.create(name="VM 1", cluster=cluster)
        cls.vminterface = cls.virtual_machine.interfaces.create(name="eth0")

        cls.virtual_chassis = VirtualChassis.objects.create(name="Chassis 1")

        cls.acl = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

    def _form(self, instance=None, **columns):
        """Build the form from the default row, with None removing a column."""
        data = {
            "access_list": self.acl.name,
            "assigned_object_type": "dcim.device",
            "assigned_object": self.device1.name,
            "direction": ACLAssignmentDirectionChoices.DIRECTION_NONE,
        }
        data.update(columns)
        return ACLAssignmentImportForm(
            data={key: value for key, value in data.items() if value is not None},
            instance=instance,
        )

    def test_host_resolves_by_name(self):
        """Test that a device row resolves from the device name."""
        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().assigned_object, self.device1)

    def test_interface_resolves_by_name_and_parent(self):
        """Test that an interface row resolves from its name and its device."""
        form = self._form(
            assigned_object_type="dcim.interface",
            assigned_object=self.interface1.name,
            assigned_object_parent=self.device1.name,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().assigned_object, self.interface1)

    def test_vm_interface_resolves_by_name_and_parent(self):
        """Test that a VM interface row resolves from its name and its virtual machine."""
        form = self._form(
            assigned_object_type="virtualization.vminterface",
            assigned_object=self.vminterface.name,
            assigned_object_parent=self.virtual_machine.name,
            direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().assigned_object, self.vminterface)

    def test_virtual_chassis_resolves_by_name(self):
        """The virtual chassis lookup value is exercised, not just its key in the drift test."""
        form = self._form(assigned_object_type="dcim.virtualchassis", assigned_object=self.virtual_chassis.name)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().assigned_object, self.virtual_chassis)

    def test_virtual_machine_resolves_by_name(self):
        """The virtual machine lookup value is exercised, not just its key in the drift test."""
        form = self._form(
            assigned_object_type="virtualization.virtualmachine",
            assigned_object=self.virtual_machine.name,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().assigned_object, self.virtual_machine)

    def test_id_without_type_is_rejected(self):
        """A create row giving only an ID names the type column, not a model field."""
        form = self._form(assigned_object=None, assigned_object_type="", assigned_object_id=str(self.device1.pk))
        self.assertFalse(form.is_valid())
        self.assertIn("must be specified", str(form.errors["assigned_object_type"]))

    def test_parent_with_an_id_is_rejected(self):
        """A parent qualifies the value column, so it contradicts an ID."""
        form = self._form(
            assigned_object_type="dcim.interface",
            assigned_object=None,
            assigned_object_parent=self.device1.name,
            assigned_object_id=str(self.interface1.pk),
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("cannot be given with", str(form.errors["assigned_object_parent"]))

    def test_wrong_parent_names_the_parent_in_the_error(self):
        """A miss under a parent must not claim the object itself does not exist."""
        form = self._form(
            assigned_object_type="dcim.interface",
            assigned_object=self.interface1.name,
            assigned_object_parent="no-such-device",
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("no-such-device", str(form.errors["assigned_object"]))

    def test_repeated_interface_name_without_parent_is_ambiguous(self):
        """Test that an interface name shared by two devices is rejected without a parent."""
        form = self._form(
            assigned_object_type="dcim.interface",
            assigned_object=self.interface1.name,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Multiple", str(form.errors["assigned_object"]))

    def test_repeated_interface_name_with_parent_picks_that_device(self):
        """Test that the parent column selects between two interfaces of the same name."""
        form = self._form(
            assigned_object_type="dcim.interface",
            assigned_object=self.interface2.name,
            assigned_object_parent=self.device2.name,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().assigned_object, self.interface2)

    def test_object_id_alone_resolves(self):
        """Test that a numeric ID resolves without a value column."""
        form = self._form(assigned_object=None, assigned_object_id=str(self.device1.pk))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().assigned_object, self.device1)

    def test_value_and_id_are_mutually_exclusive(self):
        """Test that giving both a value and an ID is rejected."""
        form = self._form(assigned_object_id=str(self.device1.pk))
        self.assertFalse(form.is_valid())
        self.assertIn("mutually exclusive", str(form.errors["assigned_object"]))

    def test_value_without_type_is_rejected(self):
        """Test that a value with no object type names the type column in its error."""
        form = self._form(assigned_object_type="")
        self.assertFalse(form.is_valid())
        self.assertIn("assigned_object_type must be specified", str(form.errors["assigned_object"]))

    def test_type_without_value_or_id_is_rejected(self):
        """Test that an object type alone is rejected."""
        form = self._form(assigned_object=None)
        self.assertFalse(form.is_valid())
        self.assertIn("assigned_object_id", str(form.errors["assigned_object"]))

    def test_parent_on_a_host_type_is_rejected(self):
        """Test that a parent qualifier is rejected for a type that has none."""
        form = self._form(assigned_object_parent=self.device1.name)
        self.assertFalse(form.is_valid())
        self.assertIn("no parent qualifier", str(form.errors["assigned_object_parent"]))

    def test_disallowed_type_is_rejected(self):
        """Test that a type outside the assignment content type filter is rejected."""
        form = self._form(assigned_object_type="ipam.prefix")
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid object type", str(form.errors["assigned_object_type"]))

    def test_unknown_object_id_is_rejected(self):
        """Test that an ID matching no object is rejected."""
        form = self._form(assigned_object=None, assigned_object_id=str(UNRESOLVABLE_CONTENT_TYPE_ID))
        self.assertFalse(form.is_valid())
        self.assertIn("not found", str(form.errors["assigned_object_id"]))

    def test_duplicate_acl_name_on_the_same_host_is_rejected(self):
        """Test that the model's per-host name rule fires through the import form."""
        self.assertTrue(self._form().is_valid())
        self._form().save()

        form = self._form()
        self.assertFalse(form.is_valid())
        self.assertIn("access_list", form.errors)

    def test_host_direction_is_normalized_to_none(self):
        """Test that a host row storing ingress is normalized by the model."""
        form = self._form(direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().direction, ACLAssignmentDirectionChoices.DIRECTION_NONE)

    def test_update_without_object_columns_keeps_the_target(self):
        """Test that an update omitting every object column preserves the stored target."""
        assignment = self._form().save()

        form = ACLAssignmentImportForm(data={"comments": "updated"}, instance=assignment)
        # BulkImportView deletes every field the record omits.
        for name in (
            "access_list",
            "assigned_object_type",
            "assigned_object",
            "assigned_object_parent",
            "assigned_object_id",
            "direction",
        ):
            del form.fields[name]

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().assigned_object, self.device1)

    def test_update_by_id_alone_moves_the_target(self):
        """Test that an update carrying only an ID moves the target within the stored type."""
        assignment = self._form().save()

        form = ACLAssignmentImportForm(data={"assigned_object_id": str(self.device2.pk)}, instance=assignment)
        for name in ("access_list", "assigned_object_type", "assigned_object", "assigned_object_parent", "direction"):
            del form.fields[name]

        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertEqual(updated.assigned_object, self.device2)
        self.assertEqual(updated.assigned_object_type, ContentType.objects.get_for_model(Device))

    def test_update_with_only_a_parent_reports_a_field_error(self):
        """An update row carrying only a parent must be a field error, not an exception."""
        assignment = self._form().save()

        form = ACLAssignmentImportForm(
            data={"assigned_object_parent": self.device1.name},
            instance=assignment,
        )
        # BulkImportView deletes every field the record omits.
        for name in ("access_list", "assigned_object_type", "assigned_object", "assigned_object_id", "direction"):
            del form.fields[name]

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)
