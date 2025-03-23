from dcim.models import Interface
from django.core.exceptions import ValidationError
from virtualization.models import VMInterface

from netbox_acls.models import AccessList, ACLInterfaceAssignment

from .base import BaseTestCase


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

    def test_acl_interface_assignment_success(self):
        """
        Test that ACLInterfaceAssignment passes validation if the ACL is assigned to the host
        and not already assigned to the interface and direction.
        """
        device_acl = AccessList(
            name="STANDARD_ACL",
            assigned_object=self.device1,
            type="standard",
            default_action="permit",
            comments="STANDARD_ACL",
        )
        device_acl.save()
        acl_device_interface = ACLInterfaceAssignment(
            access_list=device_acl,
            direction="ingress",
            assigned_object=self.device_interface1,
        )
        acl_device_interface.full_clean()

    def test_acl_interface_assignment_fail(self):
        """
        Test that ACLInterfaceAssignment passes validation if the ACL is assigned to the host
        and not already assigned to the vminterface and direction.
        """
        device_acl = AccessList(
            name="STANDARD_ACL",
            assigned_object=self.device1,
            type="standard",
            default_action="permit",
            comments="STANDARD_ACL",
        )
        device_acl.save()
        acl_vm_interface = ACLInterfaceAssignment(
            access_list=device_acl,
            direction="ingress",
            assigned_object=self.vm_interface1,
        )
        with self.assertRaises(ValidationError):
            acl_vm_interface.full_clean()

    def test_acl_vminterface_assignment_success(self):
        """
        Test that ACLInterfaceAssignment passes validation if the ACL is assigned to the host
        and not already assigned to the vminterface and direction.
        """
        vm_acl = AccessList(
            name="STANDARD_ACL",
            assigned_object=self.virtual_machine1,
            type="standard",
            default_action="permit",
            comments="STANDARD_ACL",
        )
        vm_acl.save()
        acl_vm_interface = ACLInterfaceAssignment(
            access_list=vm_acl,
            direction="ingress",
            assigned_object=self.vm_interface1,
        )
        acl_vm_interface.full_clean()

    def test_acl_host_interface_assignment_fail(self):
        """
        Test that ACLInterfaceAssignment fails validation if the ACL is not assigned to the parent host.
        """
        pass
        # TODO: test_acl_interface_assignment_fail - VM & Device

    def test_duplicate_assignment_fail(self):
        """
        Test that ACLInterfaceAssignment fails validation
        if the ACL already is assigned to the same interface and direction.
        """
        pass
        # TODO: test_duplicate_assignment_fail - VM & Device

    def test_acl_already_assigned_fail(self):
        """
        Test that ACLInterfaceAssignment fails validation
        if the interface already has an ACL assigned in the same direction.
        """
        pass
        # TODO: test_acl_already_assigned_fail - VM & Device

    # TODO: Test choices for ACLInterfaceAssignment Model
