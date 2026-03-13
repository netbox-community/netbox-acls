from django.core.exceptions import ValidationError

from netbox_acls.choices import ACLActionChoices, ACLFamilyChoices, ACLTypeChoices
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
        cls.family = ACLFamilyChoices.FAMILY_IPV4
        cls.default_action = "deny"

        # AccessLists
        cls.standard_acl1 = AccessList.objects.create(
            name="STANDARD_ACL",
            type=cls.acl_type,
            family=cls.family,
            default_action=cls.default_action,
            comments="STANDARD_ACL",
        )
        cls.standard_acl2 = AccessList.objects.create(
            name="STANDARD_ACL",
            type=cls.acl_type,
            family=cls.family,
            default_action=cls.default_action,
            comments="STANDARD_ACL",
        )
        cls.standard_acl_v6 = AccessList.objects.create(
            name="STANDARD_ACL_V6",
            type=cls.acl_type,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=cls.default_action,
            comments="STANDARD_ACL_V6",
        )
        cls.standard_acl_dual = AccessList.objects.create(
            name="STANDARD_ACL_DUAL",
            type=cls.acl_type,
            family=ACLFamilyChoices.FAMILY_DUAL,
            default_action=cls.default_action,
            comments="STANDARD_ACL_DUAL",
        )

    def test_acl_standard_rule_creation_success(self):
        """
        Test that ACLStandardRule creation passes validation.
        """
        created_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            sequence=10,
            action="permit",
            remark="",
            source=None,
            description="Created rule with any source",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.sequence, 10)
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
            sequence=20,
            action="permit",
            remark="",
            source=self.prefix1,
            description="Created rule with source prefix",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.sequence, 20)
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
            sequence=30,
            action="remark",
            remark="Test remark",
            source=None,
            description="Created rule with remark",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.sequence, 30)
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
            sequence=40,
            action="permit",
            remark="",
            source=self.aggregate1,
            description="Created rule with source aggregate",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.sequence, 40)
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
            sequence=50,
            action="permit",
            remark="",
            source=self.ip_address1,
            description="Created rule with source ip address",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.sequence, 50)
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
            sequence=60,
            action="permit",
            remark="",
            source=self.ip_range1,
            description="Created rule with source ip range",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.sequence, 60)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.ip_range1)
        self.assertEqual(created_rule.description, "Created rule with source ip range")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_standard_rule_action_permit_with_remark_success(self):
        """
        Test that ACLStandardRule with action 'permit' and remark passes validation.
        """
        created_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            sequence=70,
            action="permit",
            remark="Inline remark",
            source=None,
            description="Created permit rule with remark",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLStandardRule), True)
        self.assertEqual(created_rule.sequence, 70)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "Inline remark")
        self.assertEqual(created_rule.description, "Created permit rule with remark")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_standard_rule_action_permit_with_shared_index_action_remark_fail(self):
        """
        Test that ACLStandardRule rejects a standalone remark sharing the same sequence as a permit rule.
        """
        created_permit_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            sequence=80,
            action="permit",
            remark="",
            source=None,
            description="Created permit rule with same sequence as remark",
        )
        created_permit_rule.full_clean()
        created_permit_rule.save()

        created_remark_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            sequence=80,
            action="remark",
            remark="Standalone remark",
            source=None,
            description="Created remark rule with same sequence as permit rule",
        )
        with self.assertRaises(ValidationError):
            created_remark_rule.full_clean()

    def test_access_list_extended_to_acl_standard_rule_assignment_fail(self):
        """
        Test that Extended Access List cannot be assigned to ACLStandardRule.
        """
        extended_acl1 = AccessList.objects.create(
            name="EXTENDED_ACL",
            type=ACLTypeChoices.TYPE_EXTENDED,
            default_action=self.default_action,
            comments="EXTENDED_ACL",
        )
        standard_rule = ACLStandardRule(
            access_list=extended_acl1,
            sequence=30,
            action="remark",
            remark="Test remark",
            source=None,
            description="Created rule with remark",
        )
        with self.assertRaises(ValidationError):
            standard_rule.full_clean()

    def test_duplicate_index_per_acl_fail(self):
        """
        Test that the rule sequence must be unique per AccessList.
        """
        params = {
            "access_list": self.standard_acl1,
            "sequence": 10,
            "action": "permit",
        }
        rule_1 = ACLStandardRule(**params)
        rule_1.full_clean()
        rule_1.save()
        rule_2 = ACLStandardRule(**params)
        with self.assertRaises(ValidationError):
            rule_2.full_clean()

    def test_acl_standard_rule_action_remark_with_no_remark_fail(self):
        """
        Test that ACLStandardRule with action 'remark' and without remark fails validation.
        """
        invalid_rule = ACLStandardRule(
            access_list=self.standard_acl1,
            sequence=10,
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
            sequence=10,
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
            sequence=10,
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
                sequence=10,
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
            sequence=10,
            action=invalid_acl_rule_action_choice,
            description=f"INVALID ACL RULE ACTION CHOICES USED: action={invalid_acl_rule_action_choice}",
        )

        with self.assertRaises(ValidationError):
            invalid_acl_rule_action.full_clean()

    def test_acl_standard_rule_family_v4_acl_rejects_v6_objects(self):
        """
        Test that IPv4 ACL must not accept rules carrying IPv6 objects.
        """
        acl_v4 = AccessList.objects.create(
            name="RF4",
            type=self.acl_type,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=self.default_action,
        )
        invalid_rule = ACLStandardRule(
            access_list=acl_v4,
            sequence=10,
            action=ACLActionChoices.ACTION_PERMIT,
            source=self.prefix1_v6,
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_standard_rule_family_v6_acl_rejects_v4_objects(self):
        """
        Test that IPv6 ACL must not accept rules carrying IPv4 objects.
        """
        acl = AccessList.objects.create(
            name="RF6",
            type=self.acl_type,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=self.default_action,
        )
        invalid_rule = ACLStandardRule(
            access_list=acl,
            sequence=10,
            action=ACLActionChoices.ACTION_PERMIT,
            source=self.prefix1,
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()
