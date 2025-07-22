from django.core.exceptions import ValidationError

from netbox_acls.choices import ACLTypeChoices
from netbox_acls.models import AccessList, ACLStandardRule

from .base import BaseTestCase


class TestACLStandardRule(BaseTestCase):
    """
    Test ACLStandardRule model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Extend BaseTestCase's setUpTestData() to create additional data for testing.
        """
        super().setUpTestData()

        cls.acl_type = ACLTypeChoices.TYPE_STANDARD
        cls.default_action = "deny"

        # AccessLists
        cls.standard_acl1 = AccessList.objects.create(
            name="STANDARD_ACL",
            assigned_object=cls.device1,
            type=cls.acl_type,
            default_action=cls.default_action,
            comments="STANDARD_ACL",
        )
        cls.standard_acl2 = AccessList.objects.create(
            name="STANDARD_ACL",
            assigned_object=cls.virtual_machine1,
            type=cls.acl_type,
            default_action=cls.default_action,
            comments="STANDARD_ACL",
        )

    def test_acl_standard_rule_creation_success(self):
        """
        Test that ACLStandardRule creation passes validation.
        """
        created_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=10,
            action="permit",
            remark="",
            source_prefix=None,
            description="Created rule with any source prefix",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 10)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, None)
        self.assertEqual(created_rule.description, "Created rule with any source prefix")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_standard_rule_source_prefix_creation_success(self):
        """
        Test that ACLStandardRule with source prefix creation passes validation.
        """
        created_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=20,
            action="permit",
            remark="",
            source_prefix=self.prefix1,
            description="Created rule with source prefix",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 20)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, self.prefix1)
        self.assertEqual(created_rule.description, "Created rule with source prefix")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_standard_rule_remark_creation_success(self):
        """
        Test that ACLStandardRule with remark creation passes validation.
        """
        created_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=30,
            action="remark",
            remark="Test remark",
            source_prefix=None,
            description="Created rule with remark",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 30)
        self.assertEqual(created_rule.action, "remark")
        self.assertEqual(created_rule.remark, "Test remark")
        self.assertEqual(created_rule.source_prefix, None)
        self.assertEqual(created_rule.description, "Created rule with remark")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_access_list_extended_to_acl_standard_rule_assignment_fail(self):
        """
        Test that Extended Access List cannot be assigned to ACLStandardRule.
        """
        extended_acl1 = AccessList.objects.create(
            name="EXTENDED_ACL",
            assigned_object=self.device1,
            type=ACLTypeChoices.TYPE_EXTENDED,
            default_action=self.default_action,
            comments="EXTENDED_ACL",
        )
        standard_rule = ACLStandardRule(
            access_list=extended_acl1,
            index=30,
            action="remark",
            remark="Test remark",
            source_prefix=None,
            description="Created rule with remark",
        )
        with self.assertRaises(ValidationError):
            standard_rule.full_clean()

    def test_duplicate_index_per_acl_fail(self):
        """
        Test that the rule index must be unique per AccessList.
        """
        params = {
            "access_list": self.standard_acl1,
            "index": 10,
            "action": "permit",
        }
        rule_1 = ACLStandardRule(**params)
        rule_1.full_clean()
        rule_1.save()
        rule_2 = ACLStandardRule(**params)
        with self.assertRaises(ValidationError):
            rule_2.full_clean()

    def test_acl_standard_rule_action_permit_with_remark_fail(self):
        """
        Test that ACLStandardRule with action 'permit' and remark fails validation.
        """
        invalid_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=10,
            action="permit",
            remark="Remark",
            source_prefix=None,
            description="Invalid rule with action 'permit' and remark",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_standard_rule_action_remark_with_no_remark_fail(self):
        """
        Test that ACLStandardRule with action 'remark' and without remark fails validation.
        """
        invalid_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=10,
            action="remark",
            remark="",
            source_prefix=None,
            description="Invalid rule with action 'remark' and without remark",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_standard_rule_action_remark_with_source_prefix_fail(self):
        """
        Test that ACLStandardRule with action 'remark' and source prefix fails validation.
        """
        invalid_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=10,
            action="remark",
            remark="",
            source_prefix=self.prefix1,
            description="Invalid rule with action 'remark' and source prefix",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_valid_acl_rule_action_choices(self):
        """
        Test ACLStandardRule action choices using VALID choices.
        """
        valid_acl_rule_action_choices = ["deny", "permit", "remark"]

        for action_choice in valid_acl_rule_action_choices:
            valid_acl_rule_action = ACLStandardRule(
                access_list=self.standard_acl1,
                index=10,
                action=action_choice,
                remark="Remark" if action_choice == "remark" else None,
                description=f"VALID ACL RULE ACTION CHOICES USED: action={action_choice}",
            )
            valid_acl_rule_action.full_clean()

    def test_invalid_acl_rule_action_choices(self):
        """
        Test ACLStandardRule action choices using INVALID choices.
        """
        invalid_acl_rule_action_choice = "both"

        invalid_acl_rule_action = ACLStandardRule(
            access_list=self.standard_acl1,
            index=10,
            action=invalid_acl_rule_action_choice,
            description=f"INVALID ACL RULE ACTION CHOICES USED: action={invalid_acl_rule_action_choice}",
        )

        with self.assertRaises(ValidationError):
            invalid_acl_rule_action.full_clean()
