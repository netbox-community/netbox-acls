from django.core.exceptions import ValidationError

from dcim.models import Device, Interface, VirtualChassis
from virtualization.models import VirtualMachine, VMInterface

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLAssignment
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
        cls.acl_standard_v6 = AccessList.objects.create(
            name="STANDARD_ACL_V6",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=ACLActionChoices.ACTION_PERMIT,
            comments="STANDARD_ACL_V6",
        )
        cls.acl_standard_dual = AccessList.objects.create(
            name="STANDARD_ACL_DUAL",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_DUAL,
            default_action=ACLActionChoices.ACTION_PERMIT,
            comments="STANDARD_ACL_DUAL",
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

    def test_acl_assignment_denormalized_family_mirrors_acl_on_creation(self):
        """
        Test that ACLAssignment denormalized family mirrors ACL on creation.
        """
        acl_assignment = ACLAssignment(
            access_list=self.acl_standard1,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        acl_assignment.full_clean()
        acl_assignment.save()
        self.assertEqual(acl_assignment.family, ACLFamilyChoices.FAMILY_IPV4)

    def test_acl_assignment_interface_uniqueness_by_family_and_dual_conflicts(self):
        """
        Test that ACLAssignment interface uniqueness by family and dual conflicts.
        """
        # Put IPv4 on ingress
        ACLAssignment.objects.create(
            access_list=self.acl_standard1,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        # Second IPv4 on the same interface+direction-> rejected
        with self.assertRaises(ValidationError):
            ACLAssignment(
                access_list=self.acl_standard2,
                assigned_object=self.device_interface1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
            ).full_clean()

        # IPv6 on same interface+direction -> allowed
        ACLAssignment.objects.create(
            access_list=self.acl_standard_v6,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        # Dual on the same interface+direction-> rejected
        # (conflicts with v4/v6 present)
        with self.assertRaises(ValidationError):
            ACLAssignment(
                access_list=self.acl_standard_dual,
                assigned_object=self.device_interface1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
            ).full_clean()

    def test_acl_assignment_multiple_same_name_acls_but_unique_within_family(self):
        """
        Test that ACLAssignment multiple names acl but the same family is unique.
        """

        # Same name in different families -> allowed
        acl_v4 = AccessList.objects.create(
            name="ACL1",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        acl_v6 = AccessList.objects.create(
            name="ACL1",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        acl_v4_same_name = AccessList.objects.create(
            name="ACL1",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        ACLAssignment.objects.create(
            access_list=acl_v4,
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )
        ACLAssignment.objects.create(
            access_list=acl_v6,
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )

        # Same name, same family on the same host-> rejected
        with self.assertRaises(ValidationError):
            ACLAssignment(
                access_list=acl_v4_same_name,
                assigned_object=self.device1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
            ).full_clean()

    def test_denormalized_family_syncs_after_acl_family_change(self):
        """
        Test denormalized family sync after ACL family change.
        """
        acl = AccessList.objects.create(
            name="AccessList-Family-Sync",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        assignment = ACLAssignment.objects.create(
            access_list=acl,
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV4)

        # Flip to IPv6 — allowed for host-only; should mirror on assignment after save()
        acl.family = ACLFamilyChoices.FAMILY_IPV6
        acl.full_clean()
        acl.save()
        assignment.refresh_from_db()
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV6)

    def test_acl_assignment_ipv4_and_ipv6_allowed_on_same_interface(self):
        """
        Test that ACLAssignment IPv4 and IPv6 are allowed on the same interface.
        """
        # Create IPv4 ACL assignment
        ipv4_assignment = ACLAssignment.objects.create(
            access_list=self.acl_standard1,  # IPv4
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        # Create IPv6 ACL assignment on the same interface+direction - should succeed
        ipv6_assignment = ACLAssignment.objects.create(
            access_list=self.acl_standard_v6,  # IPv6
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        self.assertEqual(ipv4_assignment.family, ACLFamilyChoices.FAMILY_IPV4)
        self.assertEqual(ipv6_assignment.family, ACLFamilyChoices.FAMILY_IPV6)

        # Verify both exist
        assignments = ACLAssignment.objects.filter(
            assigned_object_id=self.device_interface1.pk,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        self.assertEqual(assignments.count(), 2)

    def test_acl_assignment_save_update_fields_keeps_family_in_sync(self):
        """
        Test that a partial save writes the derived family with the Access List.
        """
        assignment = ACLAssignment.objects.create(
            access_list=self.acl_standard1,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV4)

        assignment.access_list = self.acl_standard_v6
        assignment.save(update_fields={"access_list"})

        assignment.refresh_from_db()
        self.assertEqual(assignment.access_list_id, self.acl_standard_v6.pk)
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV6)

    def test_acl_assignment_save_update_fields_accepts_access_list_attname(self):
        """
        Test that the derived family is written when update_fields names the FK attname.
        """
        assignment = ACLAssignment.objects.create(
            access_list=self.acl_standard1,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        assignment.access_list = self.acl_standard_v6
        assignment.save(update_fields={"access_list_id"})

        assignment.refresh_from_db()
        self.assertEqual(assignment.access_list_id, self.acl_standard_v6.pk)
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV6)

    def test_acl_assignment_save_empty_update_fields_is_a_noop(self):
        """
        Test that an empty update_fields performs no write.
        """
        assignment = ACLAssignment.objects.create(
            access_list=self.acl_standard1,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        assignment.access_list = self.acl_standard_v6
        assignment.save(update_fields=[])

        assignment.refresh_from_db()
        self.assertEqual(assignment.access_list_id, self.acl_standard1.pk)
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV4)

    def test_acl_assignment_save_update_fields_ignores_unsaved_access_list(self):
        """
        Test that an unsaved Access List is not persisted through the derived family.
        """
        assignment = ACLAssignment.objects.create(
            access_list=self.acl_standard1,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        assignment.access_list = self.acl_standard_v6
        assignment.comments = "Updated"
        assignment.save(update_fields={"comments"})

        assignment.refresh_from_db()
        self.assertEqual(assignment.access_list, self.acl_standard1)
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV4)
        self.assertEqual(assignment.comments, "Updated")

    def test_acl_assignment_save_update_fields_ignores_unsaved_direction(self):
        """
        Test that a partial save leaves an unsaved direction unwritten.
        """
        assignment = ACLAssignment.objects.create(
            access_list=self.acl_standard1,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        assignment.direction = ACLAssignmentDirectionChoices.DIRECTION_EGRESS
        assignment.comments = "Updated"
        assignment.save(update_fields={"comments"})

        assignment.refresh_from_db()
        self.assertEqual(
            assignment.direction,
            ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        self.assertEqual(assignment.comments, "Updated")

    def test_clean_reports_an_unset_access_list_rather_than_raising(self):
        """
        Test that full_clean on an assignment with no access list returns a field error.
        """
        # Without a colliding assignment the interface check finds nothing either way.
        ACLAssignment.objects.create(
            access_list=self.acl_standard_dual,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        assignment = ACLAssignment(
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        with self.assertRaises(ValidationError) as context:
            assignment.full_clean()

        self.assertEqual(set(context.exception.message_dict), {"access_list"})

    def test_clean_reports_an_unset_access_list_on_a_host_target(self):
        """
        Test that a host assignment with no access list returns a field error.
        """
        assignment = ACLAssignment(
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )

        with self.assertRaises(ValidationError) as context:
            assignment.full_clean()

        self.assertIn("access_list", context.exception.message_dict)

    def test_clean_reports_an_unset_assigned_object_type_rather_than_raising(self):
        """
        Test that full_clean on an assignment with no assigned object type returns a field error.
        """
        assignment = ACLAssignment(
            access_list=self.acl_standard1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        with self.assertRaises(ValidationError) as context:
            assignment.full_clean()

        self.assertIn("assigned_object_type", context.exception.message_dict)
