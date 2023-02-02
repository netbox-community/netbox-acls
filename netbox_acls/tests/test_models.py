from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    Manufacturer,
    Site,
    VirtualChassis,
)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from ipam.models import Prefix
from netaddr import IPNetwork
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from netbox_acls.choices import *
from netbox_acls.models import *


class BaseTestCase(TestCase):
    """
    Base test case for netbox_acls models.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create base data to test using including:
          - 1 of each of the following: test site, manufacturer, device type, device role, cluster type, cluster, virtual_chassis, & virtual machine
          - 2 devices, prefixes, 2 interfaces, and 2 vminterfaces
        """

        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer 1",
            slug="manufacturer-1",
        )
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Device Type 1",
        )
        devicerole = DeviceRole.objects.create(
            name="Device Role 1",
            slug="device-role-1",
        )
        device = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=devicetype,
            device_role=devicerole,
        )
        virtual_chassis = VirtualChassis.objects.create(name="Virtual Chassis 1")
        virtual_chassis_member = Device.objects.create(
            name="VC Device",
            site=site,
            device_type=devicetype,
            device_role=devicerole,
            virtual_chassis=virtual_chassis,
            vc_position=1,
        )
        cluster_member = Device.objects.create(
            name="Cluster Device",
            site=site,
            device_type=devicetype,
            device_role=devicerole,
        )
        clustertype = ClusterType.objects.create(name="Cluster Type 1")
        cluster = Cluster.objects.create(
            name="Cluster 1",
            type=clustertype,
        )
        virtual_machine = VirtualMachine.objects.create(name="VirtualMachine 1")


class TestAccessList(BaseTestCase):
    """
    Test AccessList model.
    """

    def test_alphanumeric_plus_success(self):
        """
        Test that AccessList names with alphanumeric characters, '_', or '-' pass validation.
        """
        acl_good_name = AccessList(
            name="Testacl-good_name-1",
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,
            type=ACLTypeChoices.TYPE_EXTENDED,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )
        acl_good_name.full_clean()

    def test_duplicate_name_success(self):
        """
        Test that AccessList names can be non-unique if associated to different devices.
        """

        params = {
            "name": "GOOD-DUPLICATE-ACL",
            "type": ACLTypeChoices.TYPE_STANDARD,
            "default_action": ACLActionChoices.ACTION_PERMIT,
        }
        AccessList.objects.create(
            **params,
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,
        )
        vm_acl = AccessList(
            **params,
            assigned_object_type=ContentType.objects.get_for_model(VirtualMachine),
            assigned_object_id=1,
        )
        vm_acl.full_clean()
        vc_acl = AccessList(
            **params,
            assigned_object_type=ContentType.objects.get_for_model(VirtualChassis),
            assigned_object_id=1,
        )
        vc_acl.full_clean()

    def test_alphanumeric_plus_fail(self):
        """
        Test that AccessList names with non-alphanumeric (exluding '_' and '-') characters fail validation.
        """
        non_alphanumeric_plus_chars = " !@#$%^&*()[]{};:,./<>?\|~=+"

        for i, char in enumerate(non_alphanumeric_plus_chars, start=1):
            bad_acl_name = AccessList(
                name=f"Testacl-bad_name_{i}_{char}",
                assigned_object_type=ContentType.objects.get_for_model(Device),
                assigned_object_id=1,
                type=ACLTypeChoices.TYPE_EXTENDED,
                default_action=ACLActionChoices.ACTION_PERMIT,
                comments=f'ACL with "{char}" in name',
            )
            with self.assertRaises(ValidationError):
                bad_acl_name.full_clean()

    def test_duplicate_name_fail(self):
        """
        Test that AccessList names must be unique per device.
        """
        params = {
            "name": "FAIL-DUPLICATE-ACL",
            "assigned_object_type": ContentType.objects.get_for_model(Device),
            "assigned_object_id": 1,
            "type": ACLTypeChoices.TYPE_STANDARD,
            "default_action": ACLActionChoices.ACTION_PERMIT,
        }
        acl_1 = AccessList.objects.create(**params)
        acl_1.save()
        acl_2 = AccessList(**params)
        with self.assertRaises(ValidationError):
            acl_2.full_clean()
        #  TODO: test_duplicate_name_fail - VM & VC

    # TODO: Test choices for AccessList Model


class TestACLInterfaceAssignment(BaseTestCase):
    """
    Test ACLInterfaceAssignment model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Extend BaseTestCase's setUpTestData() to create additional data for testing.
        """
        super().setUpTestData()

        interfaces = Interface.objects.bulk_create(
            (
                Interface(name="Interface 1", device=device, type="1000baset"),
                Interface(name="Interface 2", device=device, type="1000baset"),
            )
        )
        vminterfaces = VMInterface.objects.bulk_create(
            (
                VMInterface(name="Interface 1", virtual_machine=virtual_machine),
                VMInterface(name="Interface 2", virtual_machine=virtual_machine),
            )
        )
        # prefixes = Prefix.objects.bulk_create(
        #    (
        #        Prefix(prefix=IPNetwork("10.0.0.0/24")),
        #        Prefix(prefix=IPNetwork("192.168.1.0/24")),
        #    )
        # )

    def test_acl_interface_assignment_success(self):
        """
        Test that ACLInterfaceAssignment passes validation if the ACL is assigned to the host and not already assigned to the interface and direction.
        """
        pass
        #  TODO: test_acl_interface_assignment_success - VM & Device

    def test_acl_interface_assignment_fail(self):
        """
        Test that ACLInterfaceAssignment fails validation if the ACL is not assigned to the parent host.
        """
        pass
        #  TODO: test_acl_interface_assignment_fail - VM & Device

    def test_duplicate_assignment_fail(self):
        """
        Test that ACLInterfaceAssignment fails validation if the ACL already is assigned to the same interface and direction.
        """
        pass
        #  TODO: test_duplicate_assignment_fail - VM & Device

    def test_acl_already_assinged_fail(self):
        """
        Test that ACLInterfaceAssignment fails validation if the interface already has an ACL assigned in the same direction.
        """
        pass
        ##  TODO: test_acl_already_assinged_fail - VM & Device

    # TODO: Test choices for ACLInterfaceAssignment Model
