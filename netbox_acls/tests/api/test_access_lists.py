from django.contrib.contenttypes.models import ContentType

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from utilities.testing import APIViewTestCases
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLAssignment


class AccessListAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for AccessList.
    """

    model = AccessList
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["display", "id", "name", "url"]

    @classmethod
    def setUpTestData(cls):
        """Set up Access List for API view testing."""
        access_lists = (
            AccessList(
                name="testacl1",
                type=ACLTypeChoices.TYPE_STANDARD,
                family=ACLFamilyChoices.FAMILY_IPV4,
                default_action=ACLActionChoices.ACTION_DENY,
            ),
            AccessList(
                name="testacl2",
                type=ACLTypeChoices.TYPE_EXTENDED,
                family=ACLFamilyChoices.FAMILY_IPV4,
                default_action=ACLActionChoices.ACTION_PERMIT,
            ),
            AccessList(
                name="testacl3",
                type=ACLTypeChoices.TYPE_EXTENDED,
                family=ACLFamilyChoices.FAMILY_IPV6,
                default_action=ACLActionChoices.ACTION_DENY,
            ),
        )
        AccessList.objects.bulk_create(access_lists)

        cls.create_data = [
            {
                "name": "testacl4",
                "type": ACLTypeChoices.TYPE_STANDARD,
                "family": ACLFamilyChoices.FAMILY_IPV4,
                "default_action": ACLActionChoices.ACTION_DENY,
            },
            {
                "name": "testacl5",
                "type": ACLTypeChoices.TYPE_EXTENDED,
                "family": ACLFamilyChoices.FAMILY_DUAL,
                "default_action": ACLActionChoices.ACTION_DENY,
            },
            {
                "name": "testacl6",
                "type": ACLTypeChoices.TYPE_STANDARD,
                "family": ACLFamilyChoices.FAMILY_IPV6,
                "default_action": ACLActionChoices.ACTION_PERMIT,
            },
        ]
        cls.bulk_update_data = {
            "comments": "Rule bulk update",
        }


class ACLAssignmentAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLAssignment.
    """

    model = ACLAssignment
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["access_list", "display", "id", "url"]
    user_permissions = (
        "dcim.view_site",
        "dcim.view_devicetype",
        "dcim.view_device",
        "dcim.view_interface",
        "virtualization.view_cluster",
        "virtualization.view_clustergroup",
        "virtualization.view_clustertype",
        "virtualization.view_virtualmachine",
        "virtualization.view_vminterface",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        """Set up ACL Interface Assignment for API view testing."""
        site = Site.objects.create(
            name="Site 1",
            slug="site-1",
        )

        # Device
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer 1",
            slug="manufacturer-1",
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Device Type 1",
        )
        device_role = DeviceRole.objects.create(
            name="Device Role 1",
            slug="device-role-1",
        )
        device = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=device_type,
            role=device_role,
        )
        device_interface1 = device.interfaces.create(
            name="DeviceInterface1",
            device=device,
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        device_interface2 = device.interfaces.create(
            name="DeviceInterface2",
            device=device,
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        device_interface3 = device.interfaces.create(
            name="DeviceInterface3",
            device=device,
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        # Virtual Machine
        cluster_type = ClusterType.objects.create(
            name="Cluster Type 1",
            slug="cluster-type-1",
        )
        cluster = Cluster.objects.create(
            name="Cluster 1",
            type=cluster_type,
        )
        virtual_machine = VirtualMachine.objects.create(
            name="VM 1",
            cluster=cluster,
        )
        virtual_machine_interface1 = virtual_machine.interfaces.create(
            name="eth0",
            virtual_machine=virtual_machine,
        )
        virtual_machine_interface2 = virtual_machine.interfaces.create(
            name="eth1",
            virtual_machine=virtual_machine,
        )
        virtual_machine_interface3 = virtual_machine.interfaces.create(
            name="eth2",
            virtual_machine=virtual_machine,
        )

        # AccessList
        acl1 = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        acl2 = AccessList.objects.create(
            name="testacl2",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        acl_assignments = (
            ACLAssignment(
                access_list=acl1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
                assigned_object_type=ContentType.objects.get_for_model(Interface),
                assigned_object_id=device_interface1.id,
            ),
            ACLAssignment(
                access_list=acl1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
                assigned_object=device_interface2,
            ),
            ACLAssignment(
                access_list=acl2,
                direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
                assigned_object_type=ContentType.objects.get_for_model(VMInterface),
                assigned_object_id=virtual_machine_interface1.id,
            ),
        )
        ACLAssignment.objects.bulk_create(acl_assignments)

        cls.create_data = [
            {
                "access_list": acl1.id,
                "assigned_object_type": "dcim.interface",
                "assigned_object_id": device_interface3.id,
                "direction": ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
            },
            {
                "access_list": acl2.id,
                "assigned_object_type": "virtualization.vminterface",
                "assigned_object_id": virtual_machine_interface2.id,
                "direction": ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
            },
            {
                "access_list": acl2.id,
                "assigned_object_type": "virtualization.vminterface",
                "assigned_object_id": virtual_machine_interface3.id,
                "direction": ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
            },
        ]
        cls.bulk_update_data = {
            "comments": "Rule bulk update",
        }
