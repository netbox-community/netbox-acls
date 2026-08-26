from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ...constants import ACL_ASSIGNMENT_MODELS
from ...forms import ACLAssignmentBulkEditForm, ACLAssignmentFilterForm, ACLAssignmentForm
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
