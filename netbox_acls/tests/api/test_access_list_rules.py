from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.models import Prefix
from utilities.testing import APIViewTestCases
from virtualization.models import Cluster, ClusterType, VirtualMachine

from netbox_acls.choices import *
from netbox_acls.models import *


class ACLStandardRuleAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLStandardRule.
    """

    model = ACLStandardRule
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["access_list", "display", "id", "index", "url"]
    user_permissions = (
        "dcim.view_site",
        "dcim.view_manufacturer",
        "dcim.view_devicetype",
        "dcim.view_device",
        "ipam.view_prefix",
        "virtualization.view_cluster",
        "virtualization.view_clustergroup",
        "virtualization.view_clustertype",
        "virtualization.view_virtualmachine",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        """Set up ACL Standard Rule for API view testing."""
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
            type=ACLTypeChoices.TYPE_STANDARD,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        # Prefix
        prefix1 = Prefix.objects.create(
            prefix="10.0.0.0/24",
        )
        prefix2 = Prefix.objects.create(
            prefix="10.0.1.0/24",
        )

        acl_standard_rules = (
            ACLStandardRule(
                access_list=access_list_device,
                index=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source_prefix=prefix1,
            ),
            ACLStandardRule(
                access_list=access_list_device,
                index=20,
                description="Rule 20",
                action=ACLRuleActionChoices.ACTION_REMARK,
                remark="Remark 1",
            ),
            ACLStandardRule(
                access_list=access_list_vm,
                index=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_DENY,
                source_prefix=prefix2,
            ),
        )
        ACLStandardRule.objects.bulk_create(acl_standard_rules)

        cls.create_data = [
            {
                "access_list": access_list_device.id,
                "index": 30,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_DENY,
                "source_prefix": prefix2.id,
            },
            {
                "access_list": access_list_vm.id,
                "index": 20,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_prefix": prefix1.id,
            },
            {
                "access_list": access_list_vm.id,
                "index": 30,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_REMARK,
                "remark": "Remark 2",
            },
        ]
        cls.bulk_update_data = {
            "description": "Rule bulk update",
        }


class ACLExtendedRuleAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLExtendedRule.
    """

    model = ACLExtendedRule
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["access_list", "display", "id", "index", "url"]
    user_permissions = (
        "dcim.view_site",
        "dcim.view_manufacturer",
        "dcim.view_devicetype",
        "dcim.view_device",
        "ipam.view_prefix",
        "virtualization.view_cluster",
        "virtualization.view_clustergroup",
        "virtualization.view_clustertype",
        "virtualization.view_virtualmachine",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        """Set up ACL Extended Rule for API view testing."""
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

        # AccessList
        access_list_device = AccessList.objects.create(
            name="testacl1",
            assigned_object=device,
            type=ACLTypeChoices.TYPE_EXTENDED,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        access_list_vm = AccessList.objects.create(
            name="testacl2",
            assigned_object=virtual_machine,
            type=ACLTypeChoices.TYPE_EXTENDED,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        # Prefix
        prefix1 = Prefix.objects.create(
            prefix="10.0.0.0/24",
        )
        prefix2 = Prefix.objects.create(
            prefix="10.0.1.0/24",
        )

        acl_extended_rules = (
            ACLExtendedRule(
                access_list=access_list_device,
                index=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_PERMIT,
                protocol=ACLProtocolChoices.PROTOCOL_TCP,
                source_prefix=prefix1,
                source_ports=[22, 443],
                destination_prefix=prefix1,
                destination_ports=[22, 443],
            ),
            ACLExtendedRule(
                access_list=access_list_device,
                index=20,
                description="Rule 20",
                action=ACLRuleActionChoices.ACTION_REMARK,
                remark="Remark 1",
            ),
            ACLExtendedRule(
                access_list=access_list_vm,
                index=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_DENY,
                source_prefix=prefix2,
                destination_prefix=prefix1,
            ),
        )
        ACLExtendedRule.objects.bulk_create(acl_extended_rules)

        cls.create_data = [
            {
                "access_list": access_list_device.id,
                "index": 30,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_DENY,
                "protocol": ACLProtocolChoices.PROTOCOL_UDP,
                "source_prefix": prefix2.id,
                "source_ports": [53],
                "destination_prefix": prefix2.id,
                "destination_ports": [53],
            },
            {
                "access_list": access_list_vm.id,
                "index": 20,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "protocol": ACLProtocolChoices.PROTOCOL_ICMP,
                "source_prefix": prefix1.id,
                "destination_prefix": prefix2.id,
            },
            {
                "access_list": access_list_vm.id,
                "index": 30,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_REMARK,
                "remark": "Remark 2",
            },
        ]
        cls.bulk_update_data = {
            "description": "Rule bulk update",
        }
