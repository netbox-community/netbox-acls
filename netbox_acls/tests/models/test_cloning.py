"""Tests for the attributes clone() carries into a prefilled creation form."""

from ...choices import (
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule
from .base import BaseTestCase


class TestCloneFields(BaseTestCase):
    """
    Every generic foreign key in clone_fields must clone under the names the
    creation form's GenericObjectChoiceField reads, not under its own name.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.standard_acl = AccessList.objects.create(
            name="Standard ACL",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )
        cls.extended_acl = AccessList.objects.create(
            name="Extended ACL",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )

    def assertClonesGenericForeignKey(self, instance, name, target):
        """Assert the generic foreign key clones as the two subwidget values."""
        attrs = instance.clone()
        self.assertEqual(attrs[f"{name}_content_type"], getattr(instance, f"{name}_type_id"))
        self.assertEqual(attrs[f"{name}_object_id"], target.pk)
        self.assertNotIn(name, attrs)

    def test_assignment_clones_its_target(self):
        """Test an assignment clones assigned_object as the subwidget pair."""
        assignment = ACLAssignment.objects.create(
            access_list=self.standard_acl,
            assigned_object=self.device1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
        )
        attrs = assignment.clone()
        self.assertEqual(attrs["assigned_object_content_type"], assignment.assigned_object_type_id)
        self.assertEqual(attrs["assigned_object_object_id"], self.device1.pk)
        self.assertNotIn("assigned_object", attrs)
        self.assertEqual(attrs["access_list"], self.standard_acl.pk)

    def test_standard_rule_clones_its_source(self):
        """Test a Standard rule clones source as the subwidget pair."""
        rule = ACLStandardRule.objects.create(
            access_list=self.standard_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
        )
        self.assertClonesGenericForeignKey(rule, "source", self.prefix1)

    def test_extended_rule_clones_both_roles(self):
        """Test an Extended rule clones source and destination independently."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            destination=self.ip_address1,
        )
        self.assertClonesGenericForeignKey(rule, "source", self.prefix1)
        self.assertClonesGenericForeignKey(rule, "destination", self.ip_address1)

    def test_unset_generic_foreign_key_is_omitted(self):
        """Test a rule with no source clones neither half of the pair."""
        rule = ACLStandardRule.objects.create(
            access_list=self.standard_acl,
            sequence=20,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="A remark",
        )
        attrs = rule.clone()
        self.assertNotIn("source_content_type", attrs)
        self.assertNotIn("source_object_id", attrs)
