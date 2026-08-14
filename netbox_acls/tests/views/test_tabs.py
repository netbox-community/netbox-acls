"""
Tests for the ACL assignment tabs contributed to plugin and core objects.

These views sit outside every standard NetBox test base, so nothing else reaches them.
"""

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from dcim.choices import InterfaceTypeChoices
from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Manufacturer,
    Site,
    VirtualChassis,
)
from utilities.testing import TestCase
from virtualization.models import Cluster, ClusterType, VirtualMachine

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLAssignment
from ...views import (
    AccessListACLAssignmentView,
    DeviceACLAssignmentView,
    InterfaceACLAssignmentView,
    VirtualChassisACLAssignmentView,
    VirtualMachineACLAssignmentView,
    VMInterfaceACLAssignmentView,
)


class ACLAssignmentTabTestCase(TestCase):
    """Each assignment tab lists its own parent's assignments and nothing else."""

    user_permissions = (
        "netbox_acls.view_aclassignment",
        "netbox_acls.view_accesslist",
        "dcim.view_device",
        "dcim.view_interface",
        "dcim.view_virtualchassis",
        "virtualization.view_virtualmachine",
        "virtualization.view_vminterface",
    )

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Device Type 1")
        role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        cls.device = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=device_type,
            role=role,
        )
        cls.interface = cls.device.interfaces.create(
            name="eth0",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.virtual_chassis = VirtualChassis.objects.create(name="Virtual Chassis 1")

        cluster_type = ClusterType.objects.create(name="Cluster Type 1", slug="cluster-type-1")
        cluster = Cluster.objects.create(name="Cluster 1", type=cluster_type)
        cls.virtual_machine = VirtualMachine.objects.create(name="VM 1", cluster=cluster)
        cls.vminterface = cls.virtual_machine.interfaces.create(name="eth0")

        # A second of every assignable object, so each tab has a same-model sibling to
        # exclude. Without one, a tab filtering only by content type, or not filtering at
        # all, returns the same single row as a correct one.
        cls.device2 = Device.objects.create(
            name="Device 2",
            site=site,
            device_type=device_type,
            role=role,
        )
        cls.interface2 = cls.device2.interfaces.create(
            name="eth0",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.virtual_chassis2 = VirtualChassis.objects.create(name="Virtual Chassis 2")
        cls.virtual_machine2 = VirtualMachine.objects.create(name="VM 2", cluster=cluster)
        cls.vminterface2 = cls.virtual_machine2.interfaces.create(name="eth0")

        cls.access_list = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        # A second access list, so the access list tab has assignments to exclude too.
        cls.access_list2 = AccessList.objects.create(
            name="testacl2",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        cls.assignments = cls.build_assignments(
            cls.access_list,
            (cls.device, cls.interface, cls.virtual_chassis, cls.virtual_machine, cls.vminterface),
        )
        cls.other_assignments = cls.build_assignments(
            cls.access_list2,
            (
                cls.device2,
                cls.interface2,
                cls.virtual_chassis2,
                cls.virtual_machine2,
                cls.vminterface2,
            ),
        )

    @staticmethod
    def build_assignments(access_list, targets):
        """Attach the access list to one of each assignable target type."""
        device, interface, virtual_chassis, virtual_machine, vminterface = targets
        assignments = {}
        for key, target, direction in (
            ("device", device, ACLAssignmentDirectionChoices.DIRECTION_NONE),
            ("interface", interface, ACLAssignmentDirectionChoices.DIRECTION_INGRESS),
            ("virtual_chassis", virtual_chassis, ACLAssignmentDirectionChoices.DIRECTION_NONE),
            ("virtual_machine", virtual_machine, ACLAssignmentDirectionChoices.DIRECTION_NONE),
            ("vminterface", vminterface, ACLAssignmentDirectionChoices.DIRECTION_EGRESS),
        ):
            assignments[key] = ACLAssignment.objects.create(
                access_list=access_list,
                direction=direction,
                assigned_object_type=ContentType.objects.get_for_model(target),
                assigned_object_id=target.pk,
            )
        return assignments

    def tab_cases(self):
        """
        Yield (view class, url name, parent, expected assignments) for every tab.

        Only the access list tab lives under the plugins namespace. The other five are
        registered against core models and resolve under dcim and virtualization.
        """
        return (
            (
                DeviceACLAssignmentView,
                "dcim:device_aclassignments",
                self.device,
                [self.assignments["device"]],
            ),
            (
                InterfaceACLAssignmentView,
                "dcim:interface_aclassignments",
                self.interface,
                [self.assignments["interface"]],
            ),
            (
                VirtualChassisACLAssignmentView,
                "dcim:virtualchassis_aclassignments",
                self.virtual_chassis,
                [self.assignments["virtual_chassis"]],
            ),
            (
                VirtualMachineACLAssignmentView,
                "virtualization:virtualmachine_aclassignments",
                self.virtual_machine,
                [self.assignments["virtual_machine"]],
            ),
            (
                VMInterfaceACLAssignmentView,
                "virtualization:vminterface_aclassignments",
                self.vminterface,
                [self.assignments["vminterface"]],
            ),
            (
                AccessListACLAssignmentView,
                "plugins:netbox_acls:accesslist_aclassignments",
                self.access_list,
                list(self.assignments.values()),
            ),
            (
                AccessListACLAssignmentView,
                "plugins:netbox_acls:accesslist_aclassignments",
                self.access_list2,
                list(self.other_assignments.values()),
            ),
        )

    def test_tab_lists_only_its_own_assignments(self):
        """Test that each tab narrows its children to the parent it hangs off."""
        for _view_class, url_name, parent, expected in self.tab_cases():
            with self.subTest(view=url_name, parent=parent):
                response = self.client.get(reverse(url_name, kwargs={"pk": parent.pk}))
                self.assertHttpStatus(response, 200)
                self.assertEqual(
                    {row.pk for row in response.context["table"].data},
                    {assignment.pk for assignment in expected},
                )

    def test_tab_badge_counts_the_assignments(self):
        """Test that the tab badge callback reports what the tab lists."""
        for view_class, url_name, parent, expected in self.tab_cases():
            with self.subTest(view=url_name, parent=parent):
                rendered = view_class.tab.render(parent)
                self.assertIsNotNone(rendered)
                self.assertEqual(rendered["badge"], len(expected))
