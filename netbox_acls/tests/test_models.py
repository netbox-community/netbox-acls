from itertools import cycle

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
        prefix = Prefix.objects.create(prefix="10.0.0.0/8")


class TestAccessList(BaseTestCase):
    """
    Test AccessList model.
    """

    common_acl_params = {
        "type": "extended",
        "default_action": "permit",
    }
    # device = Device.objects.first()

    def test_wrong_assigned_object_type_fail(self):
        """
        Test that AccessList cannot be assigned to an object type other than Device, VirtualChassis, VirtualMachine, or Cluster.
        """
        acl_bad_gfk = AccessList(
            name="TestACL_Wrong_GFK",
            assigned_object_type=ContentType.objects.get_for_model(Prefix),
            assigned_object_id=Prefix.objects.first(),
            **self.common_acl_params,
        )
        with self.assertRaises(ValidationError):
            acl_bad_gfk.full_clean()

    def test_alphanumeric_plus_success(self):
        """
        Test that AccessList names with alphanumeric characters, '_', or '-' pass validation.
        """
        acl_good_name = AccessList(
            name="Testacl-Good_Name-1",
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,  # TODO - replace with Device.objects.first()
            **self.common_acl_params,
        )
        acl_good_name.full_clean()
        # TODO: test_alphanumeric_plus_success - VirtualChassis, VirtualMachine & Cluster

    def test_duplicate_name_success(self):
        """
        Test that AccessList names can be non-unique if associated to different devices.
        """
        AccessList.objects.create(
            name="GOOD-DUPLICATE-ACL",
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,  # TODO - replace with Device.objects.first()
            **self.common_acl_params,
        )
        vm_acl = AccessList(
            name="GOOD-DUPLICATE-ACL",
            assigned_object_type=ContentType.objects.get_for_model(VirtualMachine),
            assigned_object_id=1,  # TODO - replace with VirtualMachine.objects.first().id,
            **self.common_acl_params,
        )
        vm_acl.full_clean()
        # TODO: test_duplicate_name_success - VirtualChassis, VirtualMachine & Cluster
        # vc_acl = AccessList(
        #    "name": "GOOD-DUPLICATE-ACL",
        #    assigned_object_type=ContentType.objects.get_for_model(VirtualChassis),
        #    **self.common_acl_params,
        # )
        # vc_acl.full_clean()

    def test_alphanumeric_plus_fail(self):
        """
        Test that AccessList names with non-alphanumeric (exluding '_' and '-') characters fail validation.
        """
        non_alphanumeric_plus_chars = " !@#$%^&*()[]{};:,./<>?\|~=+"

        for i, char in enumerate(non_alphanumeric_plus_chars, start=1):
            bad_acl_name = AccessList(
                name=f"Testacl-bad_name_{i}_{char}",
                assigned_object_type=ContentType.objects.get_for_model(Device),
                comments=f'ACL with "{char}" in name',
                **self.common_acl_params,
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
            **self.common_acl_params,
            "assigned_object_id": 1,  # TODO - replace with Device.objects.first()
        }
        acl_1 = AccessList.objects.create(**params)
        acl_1.save()
        acl_2 = AccessList(**params)
        with self.assertRaises(ValidationError):
            acl_2.full_clean()
        # TODO: test_duplicate_name_fail - VirtualChassis & Cluster

    def test_valid_acl_choices(self):
        """
        Test that AccessList action choices using VALID choices.
        """
        valid_acl_default_action_choices = ["permit", "deny"]
        valid_acl_types = ["standard", "extended"]
        if len(valid_acl_default_action_choices) > len(valid_acl_types):
            valid_acl_choices = list(
                zip(valid_acl_default_action_choices, cycle(valid_acl_types))
            )
        elif len(valid_acl_default_action_choices) < len(valid_acl_types):
            valid_acl_choices = list(
                zip(cycle(valid_acl_default_action_choices), valid_acl_types)
            )
        else:
            valid_acl_choices = list(
                zip(valid_acl_default_action_choices, valid_acl_types)
            )

        for default_action, acl_type in valid_acl_choices:
            valid_acl_choice = AccessList(
                name=f"TestACL_Valid_Choice_{default_action}_{acl_type}",
                comments=f"VALID ACL CHOICES USED: {default_action=} {acl_type=}",
                type=acl_type,
                default_action=default_action,
                assigned_object_type=ContentType.objects.get_for_model(Device),
                assigned_object_id=1,  # TODO - replace with Device.objects.first()
            )
            valid_acl_choice.full_clean()

    def test_invalid_acl_choices(self):
        """
        Test that AccessList action choices using INVALID choices.
        """
        valid_acl_types = ["standard", "extended"]
        invalid_acl_default_action_choice = "log"
        invalid_acl_default_action = AccessList(
            name=f"TestACL_Valid_Choice_{invalid_acl_default_action_choice}_{valid_acl_types[0]}",
            comments=f"INVALID ACL DEFAULT CHOICE USED: default_action='{invalid_acl_default_action_choice}'",
            type=valid_acl_types[0],
            default_action=invalid_acl_default_action_choice,
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,  # TODO - replace with Device.objects.first()
        )
        with self.assertRaises(ValidationError):
            invalid_acl_default_action.full_clean()

        valid_acl_default_action_choices = ["permit", "deny"]
        invalid_acl_type = "super-dupper-extended"
        invalid_acl_type = AccessList(
            name=f"TestACL_Valid_Choice_{valid_acl_default_action_choices[0]}_{invalid_acl_type}",
            comments=f"INVALID ACL DEFAULT CHOICE USED: type='{invalid_acl_type}'",
            type=invalid_acl_type,
            default_action=valid_acl_default_action_choices[0],
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,  # TODO - replace with Device.objects.first()
        )
        with self.assertRaises(ValidationError):
            invalid_acl_type.full_clean()


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
        device = Device.objects.first()
        interfaces = Interface.objects.bulk_create(
            (
                Interface(name="Interface 1", device=device, type="1000baset"),
                Interface(name="Interface 2", device=device, type="1000baset"),
            )
        )
        virtual_machine = VirtualMachine.objects.first()
        vminterfaces = VMInterface.objects.bulk_create(
            (
                VMInterface(name="Interface 1", virtual_machine=virtual_machine),
                VMInterface(name="Interface 2", virtual_machine=virtual_machine),
            )
        )
        prefixes = Prefix.objects.bulk_create(
            (
                Prefix(prefix=IPNetwork("10.0.0.0/24")),
                Prefix(prefix=IPNetwork("192.168.1.0/24")),
            )
        )

    def test_acl_interface_assignment_success(self):
        """
        Test that ACLInterfaceAssignment passes validation if the ACL is assigned to the host and not already assigned to the interface and direction.
        """
        device_acl = AccessList(
            name="STANDARD_ACL",
            comments="STANDARD_ACL",
            type="standard",
            default_action="permit",
            assigned_object_id=1,
            assigned_object_type=ContentType.objects.get_for_model(Device),
        )
        device_acl.save()
        acl_device_interface = ACLInterfaceAssignment(
            access_list=device_acl,
            direction="ingress",
            assigned_object_id=1,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
        )
        acl_device_interface.full_clean()

    def test_acl_vminterface_assignment_success(self):
        """
        Test that ACLInterfaceAssignment passes validation if the ACL is assigned to the host and not already assigned to the vminterface and direction.
        """
        vm_acl = AccessList(
            name="STANDARD_ACL",
            comments="STANDARD_ACL",
            type="standard",
            default_action="permit",
            assigned_object_id=1,
            assigned_object_type=ContentType.objects.get_for_model(VirtualMachine),
        )
        vm_acl.save()
        acl_vm_interface = ACLInterfaceAssignment(
            access_list=vm_acl,
            direction="ingress",
            assigned_object_id=1,
            assigned_object_type=ContentType.objects.get_for_model(VMInterface),
        )
        acl_vm_interface.full_clean()

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


# TODO: Investigate a Base model for ACLStandardRule and ACLExtendedRule


class TestACLStandardRule(BaseTestCase):
    """
    Test ACLStandardRule model.
    """

    # TODO: Develop tests for ACLStandardRule model


class ACLExtendedRule(BaseTestCase):
    """
    Test ACLExtendedRule model.
    """

    # TODO: Develop tests for ACLExtendedRule model
