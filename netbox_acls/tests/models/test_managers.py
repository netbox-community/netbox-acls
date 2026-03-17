"""
Tests for ACLRuleManager.
"""

from django.test import TestCase, override_settings

from ...choices import ACLFamilyChoices, ACLTypeChoices
from ...models import AccessList, ACLStandardRule


class TestACLRuleManager(TestCase):
    """
    Test ACLRuleManager methods.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create base data for testing the ACLRuleManager.
        """
        cls.access_list = AccessList.objects.create(
            name="TEST_ACL",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action="deny",
        )

    def test_get_next_sequence_empty_access_list(self):
        """
        Test that get_next_sequence returns the step value for an empty access list.
        """
        # The default step is 10
        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk)
        self.assertEqual(next_seq, 10)

    def test_get_next_sequence_with_existing_rules(self):
        """
        Test that get_next_sequence returns max_sequence + step when rules exist.
        """
        # Create a rule with sequence 10
        ACLStandardRule.objects.create(
            access_list=self.access_list,
            sequence=10,
            action="permit",
        )

        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk)
        self.assertEqual(next_seq, 20)

    def test_get_next_sequence_with_custom_step(self):
        """
        Test that get_next_sequence respects a custom step parameter.
        """
        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk, step=5)
        self.assertEqual(next_seq, 5)

        # Create a rule and verify the custom step is applied to existing max
        ACLStandardRule.objects.create(
            access_list=self.access_list,
            sequence=5,
            action="permit",
        )

        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk, step=5)
        self.assertEqual(next_seq, 10)

    def test_get_next_sequence_with_non_sequential_rules(self):
        """
        Test that get_next_sequence finds the max sequence regardless of order.
        """
        # Create rules with non-sequential sequences
        ACLStandardRule.objects.create(
            access_list=self.access_list,
            sequence=100,
            action="permit",
        )
        ACLStandardRule.objects.create(
            access_list=self.access_list,
            sequence=50,
            action="deny",
        )

        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk)
        self.assertEqual(next_seq, 110)  # max(100, 50) + 10

    def test_get_next_sequence_zero_step_uses_config(self):
        """
        Test that a step <= 0 falls back to plugin config.
        """
        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk, step=0)
        self.assertEqual(next_seq, 10)  # Should use default config value

        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk, step=-5)
        self.assertEqual(next_seq, 10)  # Should use default config value

    def test_get_next_sequence_none_step_uses_config(self):
        """
        Test that step=None falls back to plugin config.
        """
        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk, step=None)
        self.assertEqual(next_seq, 10)

    def test_get_next_sequence_isolates_access_lists(self):
        """
        Test that get_next_sequence only considers rules from the specified access list.
        """
        other_acl = AccessList.objects.create(
            name="OTHER_ACL",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action="deny",
        )

        # Create a rule in the other ACL with a high sequence
        ACLStandardRule.objects.create(
            access_list=other_acl,
            sequence=1000,
            action="permit",
        )

        # Original ACL should still return step value (empty)
        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk)
        self.assertEqual(next_seq, 10)

    @override_settings(PLUGINS_CONFIG={"netbox_acls": {"rule_sequence_step": 25}})
    def test_get_next_sequence_respects_plugin_config(self):
        """
        Test that get_next_sequence uses the configured rule_sequence_step.
        """
        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk)
        self.assertEqual(next_seq, 25)

        # Create a rule and verify the config step is applied
        ACLStandardRule.objects.create(
            access_list=self.access_list,
            sequence=25,
            action="permit",
        )

        next_seq = ACLStandardRule.objects.get_next_sequence(self.access_list.pk)
        self.assertEqual(next_seq, 50)
