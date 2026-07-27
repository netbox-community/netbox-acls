from itertools import cycle

from django.core.exceptions import ValidationError

from dcim.models import Interface

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import (
    AccessList,
    ACLAssignment,
    ACLExtendedRule,
    ACLStandardRule,
)
from .base import BaseTestCase


class TestAccessList(BaseTestCase):
    """
    Test AccessList model.
    """

    common_acl_params = {
        "type": ACLTypeChoices.TYPE_EXTENDED,
        "family": ACLFamilyChoices.FAMILY_IPV4,
        "default_action": ACLActionChoices.ACTION_DENY,
    }

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

    def test_accesslist_standard_creation(self):
        """
        Test that AccessList Standard creation passes validation.
        """
        acl_name = "Test-ACL-Standard-Type"

        created_acl = AccessList(
            name=acl_name,
            type="standard",
            family="ipv4",
            default_action="deny",
        )

        self.assertTrue(isinstance(created_acl, AccessList), True)
        self.assertEqual(created_acl.name, acl_name)
        self.assertEqual(created_acl.type, "standard")
        self.assertEqual(created_acl.default_action, "deny")

    def test_accesslist_extended_creation(self):
        """
        Test that AccessList Extended creation passes validation.
        """
        acl_name = "Test-ACL-Extended-Type"

        created_acl = AccessList(
            name=acl_name,
            type="extended",
            family="ipv4",
            default_action="permit",
        )

        self.assertTrue(isinstance(created_acl, AccessList))
        self.assertEqual(created_acl.name, acl_name)
        self.assertEqual(created_acl.type, "extended")
        self.assertEqual(created_acl.default_action, "permit")

    def test_alphanumeric_plus_success(self):
        """
        Test that AccessList names with alphanumeric characters, '_', or '-' pass validation.
        """
        acl_good_name = AccessList(
            name="Test-ACL-Good_Name-1",
            **self.common_acl_params,
        )
        acl_good_name.full_clean()

    def test_duplicate_name_success(self):
        """
        Test that AccessList names can be non-unique.
        """
        acl1 = AccessList(
            name="GOOD-DUPLICATE-ACL",
            **self.common_acl_params,
        )
        acl1.full_clean()

        acl2 = AccessList(
            name="GOOD-DUPLICATE-ACL",
            **self.common_acl_params,
        )
        acl2.full_clean()

    def test_valid_acl_choices(self):
        """
        Test that AccessList action choices using VALID choices.
        """
        valid_acl_default_action_choices = ["permit", "deny"]
        valid_acl_types = ["standard", "extended"]
        if len(valid_acl_default_action_choices) > len(valid_acl_types):
            valid_acl_choices = list(zip(valid_acl_default_action_choices, cycle(valid_acl_types)))
        elif len(valid_acl_default_action_choices) < len(valid_acl_types):
            valid_acl_choices = list(zip(cycle(valid_acl_default_action_choices), valid_acl_types))
        else:
            valid_acl_choices = list(zip(valid_acl_default_action_choices, valid_acl_types))

        for default_action, acl_type in valid_acl_choices:
            valid_acl_choice = AccessList(
                name=f"TestACL_Valid_Choice_{default_action}_{acl_type}",
                type=acl_type,
                family=ACLFamilyChoices.FAMILY_IPV4,
                default_action=default_action,
                comments=f"VALID ACL CHOICES USED: {default_action=} {acl_type=}",
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
            type=valid_acl_types[0],
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=invalid_acl_default_action_choice,
            comments=f"INVALID ACL DEFAULT CHOICE USED: default_action='{invalid_acl_default_action_choice}'",
        )
        with self.assertRaises(ValidationError):
            invalid_acl_default_action.full_clean()

        valid_acl_default_action_choices = ["permit", "deny"]
        invalid_acl_type = "super-dupper-extended"
        invalid_acl_type = AccessList(
            name=f"TestACL_Valid_Choice_{valid_acl_default_action_choices[0]}_{invalid_acl_type}",
            type=invalid_acl_type,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=valid_acl_default_action_choices[0],
            comments=f"INVALID ACL DEFAULT CHOICE USED: type='{invalid_acl_type}'",
        )
        with self.assertRaises(ValidationError):
            invalid_acl_type.full_clean()

    def test_acl_family_change_blocked_if_standard_rules_exist(self):
        """
        Changing the ACL family must be blocked when any rules exist (standard).
        """
        acl = AccessList.objects.create(
            name="STD",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        # Minimal valid standard rule (uses GFK "source")
        ACLStandardRule.objects.create(
            access_list=acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
        )

        acl.family = ACLFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            acl.full_clean()

    def test_acl_family_change_blocked_if_extended_rules_exist(self):
        """
        Changing the ACL family must be blocked when any rules exist (extended).
        """
        acl = AccessList.objects.create(
            name="EXT",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        ACLExtendedRule.objects.create(
            access_list=acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=None,
            destination=self.prefix1_v6,
        )

        acl.family = ACLFamilyChoices.FAMILY_IPV4
        with self.assertRaises(ValidationError):
            acl.full_clean()

    def test_acl_family_change_updates_assignments_when_allowed_host_only(self):
        """
        Test that changing the ACL family with host assignments passes validation.
        """
        acl = AccessList.objects.create(
            name="AccessList-v4",
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

        # Change to IPv6 without rules is allowed
        acl.family = ACLFamilyChoices.FAMILY_IPV6
        acl.full_clean()
        acl.save()

        assignment.refresh_from_db()
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV6)

    def test_acl_family_change_blocked_if_interface_assignment_conflicts(self):
        """
        Test that changing the ACL family is blocked if a conflicting interface assignment exists.
        """
        acl_v4 = AccessList.objects.create(
            name="AccessList-v4",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        acl_v6 = AccessList.objects.create(
            name="AccessList-v6",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # Place both ACLs (v4 and v6) on the same interface/direction
        ACLAssignment.objects.create(
            access_list=acl_v4,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        ACLAssignment.objects.create(
            access_list=acl_v6,
            assigned_object=self.device_interface1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        # Trying to change 'AccessList-v6' to DUAL must be blocked
        # (conflicts with existing v4)
        acl_v6.family = ACLFamilyChoices.FAMILY_DUAL
        with self.assertRaises(ValidationError):
            acl_v6.full_clean()

    def test_acl_family_change_on_host_blocks_duplicate_name_within_target_family(self):
        """
        Tests that changing the ACL family on a host with existing ACLs of the same name and family is blocked.
        """
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

        # Changing the family leads to a duplicate name error
        acl_v6.family = ACLFamilyChoices.FAMILY_IPV4
        with self.assertRaises(ValidationError):
            acl_v6.full_clean()

    def test_accesslist_save_blocks_host_name_rename_collision(self):
        """#358: save() must re-enforce the host name/family guard for full_clean()-skipping callers."""
        acl_a = AccessList.objects.create(
            name="ACL1",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        acl_b = AccessList.objects.create(
            name="ACL2",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        ACLAssignment.objects.create(
            access_list=acl_a,
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )
        ACLAssignment.objects.create(
            access_list=acl_b,
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )

        # Rename acl_b to collide with acl_a on the same host + family, bypassing full_clean()
        acl_b.name = "ACL1"
        with self.assertRaises(ValidationError):
            acl_b.save()

    def _create_host_assigned_acl_pair(self, family_b=ACLFamilyChoices.FAMILY_IPV4):
        """
        Creates ACL1 (IPv4) and ACL2 (in the given family), both assigned to the same host.
        """
        acl_a = AccessList.objects.create(
            name="ACL1",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        acl_b = AccessList.objects.create(
            name="ACL2",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=family_b,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        for access_list in (acl_a, acl_b):
            ACLAssignment.objects.create(
                access_list=access_list,
                assigned_object=self.device1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
            )
        return acl_a, acl_b

    def test_accesslist_save_update_fields_ignores_unsaved_name(self):
        """
        Test that a colliding name left out of update_fields does not trigger the rename guard.
        """
        acl_a, acl_b = self._create_host_assigned_acl_pair()

        acl_b.name = acl_a.name
        acl_b.comments = "Updated"
        acl_b.save(update_fields={"comments"})

        acl_b.refresh_from_db()
        self.assertEqual(acl_b.name, "ACL2")
        self.assertEqual(acl_b.comments, "Updated")

    def test_accesslist_save_update_fields_enforces_saved_name(self):
        """
        Test that a colliding name included in update_fields is still rejected.
        """
        acl_a, acl_b = self._create_host_assigned_acl_pair()

        acl_b.name = acl_a.name
        with self.assertRaises(ValidationError):
            acl_b.save(update_fields={"name"})

    def test_accesslist_save_update_fields_ignores_unsaved_family(self):
        """
        Test that a family change left out of update_fields does not re-sync the assignments.
        """
        acl = AccessList.objects.create(
            name="ACL1",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        assignment = ACLAssignment.objects.create(
            access_list=acl,
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )

        acl.family = ACLFamilyChoices.FAMILY_IPV6
        acl.comments = "Updated"
        acl.save(update_fields={"comments"})

        acl.refresh_from_db()
        assignment.refresh_from_db()
        self.assertEqual(acl.comments, "Updated")
        self.assertEqual(acl.family, ACLFamilyChoices.FAMILY_IPV4)
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV4)

    def test_accesslist_save_update_fields_syncs_saved_family(self):
        """
        Test that a family change included in update_fields re-syncs the assignments.
        """
        acl = AccessList.objects.create(
            name="ACL1",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        assignment = ACLAssignment.objects.create(
            access_list=acl,
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )

        acl.family = ACLFamilyChoices.FAMILY_IPV6
        acl.save(update_fields={"family"})

        acl.refresh_from_db()
        assignment.refresh_from_db()
        self.assertEqual(acl.family, ACLFamilyChoices.FAMILY_IPV6)
        self.assertEqual(assignment.family, ACLFamilyChoices.FAMILY_IPV6)

    def test_accesslist_save_update_fields_ignores_unsaved_type(self):
        """
        Test that a type change left out of update_fields does not trigger the rules guard.
        """
        acl = AccessList.objects.create(
            name="ACL1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        ACLStandardRule.objects.create(
            access_list=acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
        )

        acl.type = ACLTypeChoices.TYPE_EXTENDED
        acl.comments = "Updated"
        acl.save(update_fields={"comments"})

        acl.refresh_from_db()
        self.assertEqual(acl.type, ACLTypeChoices.TYPE_STANDARD)
        self.assertEqual(acl.comments, "Updated")

    def test_accesslist_save_update_fields_validates_name_against_persisted_family(self):
        """
        Test that a rename is validated against the stored family, not an unsaved one.
        """
        acl_a, acl_b = self._create_host_assigned_acl_pair(family_b=ACLFamilyChoices.FAMILY_IPV6)

        # ACL1 is IPv4 and ACL2 is IPv6, so the rename is allowed
        acl_b.family = ACLFamilyChoices.FAMILY_IPV4
        acl_b.name = acl_a.name
        acl_b.save(update_fields={"name"})

        acl_b.refresh_from_db()
        self.assertEqual(acl_b.name, "ACL1")
        self.assertEqual(acl_b.family, ACLFamilyChoices.FAMILY_IPV6)
        self.assertEqual(
            ACLAssignment.objects.get(access_list=acl_b).family,
            ACLFamilyChoices.FAMILY_IPV6,
        )

    def test_accesslist_clean_tolerates_missing_row_for_pk(self):
        """
        Test that clean() skips the change guards when the pk is set but the row is gone.
        """
        acl = AccessList.objects.create(
            name="ACL-GHOST",
            **self.common_acl_params,
        )
        # Delete through the queryset so the in-memory instance keeps its pk
        AccessList.objects.filter(pk=acl.pk).delete()

        acl.full_clean()
