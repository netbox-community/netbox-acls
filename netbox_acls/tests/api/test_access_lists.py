from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from django.contrib.contenttypes.models import ContentType
from utilities.testing import APIViewTestCases
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from netbox_acls.choices import *
from netbox_acls.models import *


class AccessListAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for AccessList.
    """

    model = AccessList
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["display", "id", "name", "url"]
    user_permissions = (
        "dcim.view_site",
        "dcim.view_devicetype",
        "dcim.view_device",
        "virtualization.view_cluster",
        "virtualization.view_clustergroup",
        "virtualization.view_clustertype",
        "virtualization.view_virtualmachine",
    )

    @classmethod
    def setUpTestData(cls):
        """Set up Access List for API view testing."""
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

        access_lists = (
            AccessList(
                name="testacl1",
                assigned_object_type=ContentType.objects.get_for_model(Device),
                assigned_object_id=device.id,
                type=ACLTypeChoices.TYPE_STANDARD,
                default_action=ACLActionChoices.ACTION_DENY,
            ),
            AccessList(
                name="testacl2",
                assigned_object=device,
                type=ACLTypeChoices.TYPE_EXTENDED,
                default_action=ACLActionChoices.ACTION_PERMIT,
            ),
            AccessList(
                name="testacl3",
                assigned_object_type=ContentType.objects.get_for_model(VirtualMachine),
                assigned_object_id=virtual_machine.id,
                type=ACLTypeChoices.TYPE_EXTENDED,
                default_action=ACLActionChoices.ACTION_DENY,
            ),
        )
        AccessList.objects.bulk_create(access_lists)

        cls.create_data = [
            {
                "name": "testacl4",
                "assigned_object_type": "dcim.device",
                "assigned_object_id": device.id,
                "type": ACLTypeChoices.TYPE_STANDARD,
                "default_action": ACLActionChoices.ACTION_DENY,
            },
            {
                "name": "testacl5",
                "assigned_object_type": "dcim.device",
                "assigned_object_id": device.id,
                "type": ACLTypeChoices.TYPE_EXTENDED,
                "default_action": ACLActionChoices.ACTION_DENY,
            },
            {
                "name": "testacl6",
                "assigned_object_type": "virtualization.virtualmachine",
                "assigned_object_id": virtual_machine.id,
                "type": ACLTypeChoices.TYPE_STANDARD,
                "default_action": ACLActionChoices.ACTION_PERMIT,
            },
        ]
        cls.bulk_update_data = {
            "default_action": ACLActionChoices.ACTION_PERMIT,
        }


class ACLInterfaceAssignmentAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLInterfaceAssignment.
    """

    model = ACLInterfaceAssignment
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
        access_list_device = AccessList.objects.create(
            name="testacl1",
            assigned_object=device,
            type=ACLTypeChoices.TYPE_STANDARD,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        access_list_vm = AccessList.objects.create(
            name="testacl2",
            assigned_object=virtual_machine,
            type=ACLTypeChoices.TYPE_EXTENDED,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        acl_interface_assignments = (
            ACLInterfaceAssignment(
                access_list=access_list_device,
                direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
                assigned_object_type=ContentType.objects.get_for_model(Interface),
                assigned_object_id=device_interface1.id,
            ),
            ACLInterfaceAssignment(
                access_list=access_list_device,
                direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
                assigned_object=device_interface2,
            ),
            ACLInterfaceAssignment(
                access_list=access_list_vm,
                direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
                assigned_object_type=ContentType.objects.get_for_model(VMInterface),
                assigned_object_id=virtual_machine_interface1.id,
            ),
        )
        ACLInterfaceAssignment.objects.bulk_create(acl_interface_assignments)

        cls.create_data = [
            {
                "access_list": access_list_device.id,
                "assigned_object_type": "dcim.interface",
                "assigned_object_id": device_interface3.id,
                "direction": ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
            },
            {
                "access_list": access_list_vm.id,
                "assigned_object_type": "virtualization.vminterface",
                "assigned_object_id": virtual_machine_interface2.id,
                "direction": ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
            },
            {
                "access_list": access_list_vm.id,
                "assigned_object_type": "virtualization.vminterface",
                "assigned_object_id": virtual_machine_interface3.id,
                "direction": ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
            },
        ]
