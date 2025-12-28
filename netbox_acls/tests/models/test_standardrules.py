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
            source=None,
            description="Created rule with any source",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 10)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.description, "Created rule with any source")
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
            source=self.prefix1,
            description="Created rule with source prefix",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 20)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.prefix1)
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
            source=None,
            description="Created rule with remark",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 30)
        self.assertEqual(created_rule.action, "remark")
        self.assertEqual(created_rule.remark, "Test remark")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.description, "Created rule with remark")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_standard_rule_source_aggregate_creation_success(self):
        """
        Test that ACLStandardRule with source aggregate creation passes validation.
        """
        created_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=40,
            action="permit",
            remark="",
            source=self.aggregate1,
            description="Created rule with source aggregate",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 40)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.aggregate1)
        self.assertEqual(created_rule.description, "Created rule with source aggregate")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_standard_rule_source_ip_address_creation_success(self):
        """
        Test that ACLStandardRule with source ip address creation passes validation.
        """
        created_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=50,
            action="permit",
            remark="",
            source=self.ip_address1,
            description="Created rule with source ip address",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 50)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.ip_address1)
        self.assertEqual(created_rule.description, "Created rule with source ip address")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_standard_rule_source_ip_range_creation_success(self):
        """
        Test that ACLStandardRule with source ip range creation passes validation.
        """
        created_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            index=60,
            action="permit",
            remark="",
            source=self.ip_range1,
            description="Created rule with source ip range",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.index, 60)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.ip_range1)
        self.assertEqual(created_rule.description, "Created rule with source ip range")
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
            source=None,
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
            source=None,
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
            source=None,
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
            source=self.prefix1,
            description="Invalid rule with action 'remark' and source prefix",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_invalid_aci_standard_rule_source_object(self):
        """
        Test ACLStandardRule source object validation.
        """
        invalid_acl_rule_source_object = ACLStandardRule(
            access_list=self.standard_acl1,
            index=10,
            action="permit",
            remark="",
            source=self.device1,
            description="Rule with invalid source object",
        )
        with self.assertRaises(ValidationError):
            invalid_acl_rule_source_object.full_clean()

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
