from django.core.exceptions import ValidationError
from virtualization.models import VirtualMachine
from dcim.models import Device, VirtualChassis, Interface
from virtualization.models import VMInterface

from netbox_acls.models import AccessList, ACLAssignment

from .base import BaseTestCase


class TestACLAssignment(BaseTestCase):
    """
    Test ACLAssignment model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Extend BaseTestCase's setUpTestData() to create additional data for testing.
        """
        super().setUpTestData()

        interface_type = "1000baset"

        # Device Interfaces
        cls.device_interface1 = Interface.objects.create(
            name="Interface 1",
            device=cls.device1,
            type=interface_type,
        )
        cls.device_interface2 = Interface.objects.create(
            name="Interface 2",
            device=cls.device1,
            type=interface_type,
        )

        # Virtual Machine Interfaces
        cls.vm_interface1 = VMInterface.objects.create(
            name="Interface 1",
            virtual_machine=cls.virtual_machine1,
        )
        cls.vm_interface2 = VMInterface.objects.create(
            name="Interface 2",
            virtual_machine=cls.virtual_machine1,
        )

        # Standard ACLs
        cls.acl_standard1 = AccessList.objects.create(
            name="STANDARD_ACL_1",
            type="standard",
            default_action="permit",
            comments="STANDARD_ACL",
        )
        cls.acl_standard2 = AccessList.objects.create(
            name="STANDARD_ACL_2",
            type="standard",
            default_action="permit",
            comments="STANDARD_ACL",
        )

        # Extended ACLs
        cls.acl_extended1 = AccessList.objects.create(
            name="EXTENDED_ACL_1",
            type="extended",
            default_action="permit",
            comments="EXTENDED_ACL",
        )
        cls.acl_extended2 = AccessList.objects.create(
            name="EXTENDED_ACL_2",
            type="extended",
            default_action="permit",
            comments="EXTENDED_ACL",
        )

    def test_acl_assignment_success(self):
        """
        Test that ACLAssignment passes validation if the ACL is assigned to the host
        and not already assigned to the interface and direction.
        """
        acl_device_interface = ACLAssignment(
            access_list=self.acl_standard1,
            direction="ingress",
            assigned_object=self.device_interface1,
        )
        acl_device_interface.full_clean()

    def test_acl_assignment_with_device(self):
        """
        Test that ACLAssignment creation with an assigned device passes validation.
        """
        device_assignment = ACLAssignment(
            access_list=self.acl_standard1,
            direction="ingress",
            assigned_object=self.device1,
        )

        self.assertTrue(isinstance(device_assignment, ACLAssignment))
        self.assertEqual(device_assignment.access_list.name, self.acl_standard1.name)
        self.assertEqual(isinstance(device_assignment.assigned_object, Device), True)
        self.assertEqual(device_assignment.assigned_object, self.device1)
        self.assertEqual(device_assignment.direction, "ingress")

    def test_acl_assignment_with_device_interface(self):
        """
        Test that ACLAssignment creation with an assigned interface passes validation.
        """
        interface_assignment = ACLAssignment(
            access_list=self.acl_standard1,
            direction="ingress",
            assigned_object=self.device_interface1,
        )

        self.assertTrue(isinstance(interface_assignment, ACLAssignment))
        self.assertEqual(interface_assignment.access_list.name, self.acl_standard1.name)
        self.assertEqual(isinstance(interface_assignment.assigned_object, Interface), True)
        self.assertEqual(interface_assignment.assigned_object, self.device_interface1)
        self.assertEqual(interface_assignment.direction, "ingress")

    def test_acl_assignment_with_virtual_chassis(self):
        """
        Test that ACLAssignment creation with an assigned virtual chassis passes validation.
        """
        virtual_chassis_assignment = ACLAssignment(
            access_list=self.acl_standard1,
            direction="ingress",
            assigned_object=self.virtual_chassis1,
        )

        self.assertTrue(isinstance(virtual_chassis_assignment, ACLAssignment))
        self.assertEqual(virtual_chassis_assignment.access_list.name, self.acl_standard1.name)
        self.assertEqual(isinstance(virtual_chassis_assignment.assigned_object, VirtualChassis), True)
        self.assertEqual(virtual_chassis_assignment.assigned_object, self.virtual_chassis1)
        self.assertEqual(virtual_chassis_assignment.direction, "ingress")

    def test_acl_assignment_with_virtual_machine(self):
        """
        Test that ACLAssignment creation with an assigned virtual machine passes validation.
        """
        virtual_machine_assignment = ACLAssignment(
            access_list=self.acl_standard1,
            direction="ingress",
            assigned_object=self.virtual_machine1,
        )

        self.assertTrue(isinstance(virtual_machine_assignment, ACLAssignment))
        self.assertEqual(virtual_machine_assignment.access_list.name, self.acl_standard1.name)
        self.assertEqual(isinstance(virtual_machine_assignment.assigned_object, VirtualMachine), True)
        self.assertEqual(virtual_machine_assignment.assigned_object, self.virtual_machine1)
        self.assertEqual(virtual_machine_assignment.direction, "ingress")

    def test_acl_assignment_with_virtual_machine_interface(self):
        """
        Test that ACLAssignment creation with an assigned virtual machine interface passes validation.
        """
        virtual_machine_interface_assignment = ACLAssignment(
            access_list=self.acl_standard1,
            direction="ingress",
            assigned_object=self.vm_interface1,
        )

        self.assertTrue(isinstance(virtual_machine_interface_assignment, ACLAssignment))
        self.assertEqual(virtual_machine_interface_assignment.access_list.name, self.acl_standard1.name)
        self.assertEqual(isinstance(virtual_machine_interface_assignment.assigned_object, VMInterface), True)
        self.assertEqual(virtual_machine_interface_assignment.assigned_object, self.vm_interface1)
        self.assertEqual(virtual_machine_interface_assignment.direction, "ingress")

    def test_acl_assignment_with_duplicate_name_per_device_fail(self):
        """
        Test that AccessList names must be unique per device.
        """
        acl1_assignment = ACLAssignment(
            access_list=self.acl_standard1,
            direction="none",
            assigned_object=self.device1,
        )
        acl1_assignment.full_clean()
        acl1_assignment.save()

        acl2 = AccessList(
            name="STANDARD_ACL_1",
            type="standard",
            default_action="permit",
            comments="Same Name ACL",
        )
        acl2.save()
        acl2_assignment = ACLAssignment(
            access_list=acl2,
            direction="none",
            assigned_object=self.device1,
        )

        with self.assertRaises(ValidationError):
            acl2_assignment.full_clean()
            acl2_assignment.save()

    def test_acl_assignment_with_duplicate_interface_and_direction_fail(self):
        """
        Test that ACLAssignment fails validation
        if the ACL already is assigned to the same interface and direction.
        """
        acl_device_interface1 = ACLAssignment(
            access_list=self.acl_standard1,
            direction="ingress",
            assigned_object=self.device_interface1,
        )
        acl_device_interface1.full_clean()
        acl_device_interface1.save()
        acl_device_interface2 = ACLAssignment(
            access_list=self.acl_standard1,
            direction="ingress",
            assigned_object=self.device_interface1,
        )
        with self.assertRaises(ValidationError):
            acl_device_interface2.full_clean()

    def test_valid_acl_interface_assignment_choices(self):
        """
        Test that ACLAssignment action choices using VALID choices.
        """
        valid_acl_assignment_direction_choices = ["ingress", "egress"]

        for direction_choice in valid_acl_assignment_direction_choices:
            valid_acl_assignment = ACLAssignment(
                access_list=self.acl_standard1,
                direction=direction_choice,
                assigned_object=self.device_interface1,
                comments=f"VALID ACL ASSIGNMENT CHOICES USED: direction={direction_choice}",
            )
            valid_acl_assignment.full_clean()

    def test_invalid_acl_choices(self):
        """
        Test that ACLAssignment action choices using INVALID choices.
        """
        invalid_acl_assignment_direction_choice = "both"

        invalid_acl_assignment_direction = ACLAssignment(
            access_list=self.acl_standard1,
            direction=invalid_acl_assignment_direction_choice,
            assigned_object=self.device_interface1,
            comments=f"INVALID ACL DEFAULT CHOICE USED: default_action='{invalid_acl_assignment_direction_choice}'",
        )
        with self.assertRaises(ValidationError):
            invalid_acl_assignment_direction.full_clean()
