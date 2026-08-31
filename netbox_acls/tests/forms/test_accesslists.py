from django import forms
from django.test import TestCase

from ...choices import ACLActionChoices, ACLFamilyChoices, ACLRuleActionChoices, ACLTypeChoices
from ...forms import AccessListBulkEditForm, AccessListFilterForm, AccessListForm
from ...models import AccessList, ACLStandardRule
from .base import BulkEditFieldsetTestMixin


class AccessListFormTestCase(BulkEditFieldsetTestMixin, TestCase):
    """Form tests for AccessList forms."""

    bulk_edit_form = AccessListBulkEditForm

    @classmethod
    def setUpTestData(cls):
        cls.access_list = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            remark="",
        )

    def test_valid_minimal_form(self):
        """Test that a name, type, family and default action alone validate."""
        form = AccessListForm(
            data={
                "name": "testacl2",
                "type": ACLTypeChoices.TYPE_EXTENDED,
                "family": ACLFamilyChoices.FAMILY_IPV6,
                "default_action": ACLActionChoices.ACTION_PERMIT,
            },
        )
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

    def test_type_change_blocked_with_rules(self):
        """Test that the type cannot be changed once rules are associated."""
        form = AccessListForm(
            data={
                "name": self.access_list.name,
                "type": ACLTypeChoices.TYPE_EXTENDED,
                "family": self.access_list.family,
                "default_action": self.access_list.default_action,
            },
            instance=self.access_list,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("type", form.errors)

    def test_family_change_blocked_with_rules(self):
        """Test that the family cannot be changed once rules are associated."""
        form = AccessListForm(
            data={
                "name": self.access_list.name,
                "type": self.access_list.type,
                "family": ACLFamilyChoices.FAMILY_IPV6,
                "default_action": self.access_list.default_action,
            },
            instance=self.access_list,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("family", form.errors)

    def test_choice_filters_accept_multiple_values(self):
        """The filter form's choice fields must be multi-selects, matching the filter set."""
        form = AccessListFilterForm()
        for field_name in ("type", "family", "default_action"):
            with self.subTest(field_name=field_name):
                self.assertIsInstance(form.fields[field_name], forms.MultipleChoiceField)
