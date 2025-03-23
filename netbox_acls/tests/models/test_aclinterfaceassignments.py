from dcim.models import Device, Interface
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from virtualization.models import VirtualMachine, VMInterface

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
        # prefixes = Prefix.objects.bulk_create(
        #    (
        #        Prefix(prefix=IPNetwork("10.0.0.0/24")),
        #        Prefix(prefix=IPNetwork("192.168.1.0/24")),
        #    )
        # )

    def test_acl_interface_assignment_success(self):
        """
        Test that ACLInterfaceAssignment passes validation if the ACL is assigned to the host
        and not already assigned to the interface and direction.
        """
        device_acl = AccessList(
            name="STANDARD_ACL",
            comments="STANDARD_ACL",
            type="standard",
            default_action="permit",
            assigned_object=Device.objects.first(),
        )
        device_acl.save()
        acl_device_interface = ACLInterfaceAssignment(
            access_list=device_acl,
            direction="ingress",
            assigned_object=Interface.objects.first(),
        )
        acl_device_interface.full_clean()

    def test_aclinterface_assignment_fail(self):
        """
        Test that ACLInterfaceAssignment passes validation if the ACL is assigned to the host
        and not already assigned to the vminterface and direction.
        """
        device_acl = AccessList(
            name="STANDARD_ACL",
            comments="STANDARD_ACL",
            type="standard",
            default_action="permit",
            assigned_object=Device.objects.first(),
        )
        device_acl.save()
        acl_vm_interface = ACLInterfaceAssignment(
            access_list=device_acl,
            direction="ingress",
            assigned_object=VMInterface.objects.first(),
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
