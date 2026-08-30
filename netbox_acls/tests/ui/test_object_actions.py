"""Tests for the plugin's detail view object actions."""

from django.apps import apps
from django.test import SimpleTestCase
from django.urls import reverse

from netbox.object_actions import CloneObject, DeleteObject, EditObject
from utilities.views import get_view

from ...choices import ACLTypeChoices
from ...models import AccessList, ACLExtendedRule, ACLStandardRule
from ...object_actions import AddRule
from .base import UITestCase


class AddRuleDeclarationTestCase(SimpleTestCase):
    """Test how the access list detail view declares the Add Rule button."""

    def test_access_list_view_keeps_the_standard_object_actions(self):
        """Test declaring Add Rule did not drop clone, edit and delete."""
        actions = get_view(AccessList).actions

        self.assertEqual(actions[0], AddRule)
        for action in (CloneObject, EditObject, DeleteObject):
            with self.subTest(action=action.__name__):
                self.assertIn(action, actions)

    def test_the_action_targets_the_rule_model_matching_the_type(self):
        """Test each access list type resolves to its own rule model.

        The expected models are named here rather than read back from
        rule_models, which would make the assertion tautological.
        """
        for value, expected in (
            (ACLTypeChoices.TYPE_STANDARD, ACLStandardRule),
            (ACLTypeChoices.TYPE_EXTENDED, ACLExtendedRule),
        ):
            with self.subTest(type=value):
                self.assertEqual(AddRule.get_rule_model(AccessList(type=value)), expected)

    def test_the_action_covers_every_access_list_type(self):
        """Test no type is left without a rule model to add."""
        self.assertEqual(sorted(AddRule.rule_models), sorted(ACLTypeChoices.values()))

    def test_the_prefills_are_real_fields_on_the_rule_form(self):
        """Test every prefill key survives the form load.

        An unknown key is dropped when the form loads, so the field
        opens empty and nothing raises.
        """
        for label in AddRule.rule_models.values():
            model = apps.get_model(label)
            form = get_view(model, "edit").form
            for key in AddRule.url_params_spec:
                with self.subTest(model=model.__name__, key=key):
                    self.assertIn(key, form.base_fields)


class AddRuleRenderTestCase(UITestCase):
    """Test the Add Rule button's permission gate and type switch.

    One permission per test, because the object permission backend
    caches its result on the user the first time has_perm() runs.
    """

    @classmethod
    def setUpTestData(cls):
        """Create one access list of each type."""
        cls.standard = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
        )
        cls.extended = AccessList.objects.create(
            name="testacl2",
            type=ACLTypeChoices.TYPE_EXTENDED,
        )

    def test_the_button_renders_for_the_matching_rule_permission(self):
        """Test a user who may add the rule type gets a prefilled button."""
        self.add_permissions("netbox_acls.add_aclstandardrule")

        html = AddRule.render(self.get_context(self.standard), self.standard)

        self.assertIn(reverse("plugins:netbox_acls:aclstandardrule_add"), html)
        self.assertIn(f"access_list={self.standard.pk}", html)

    def test_the_button_is_hidden_without_the_rule_permission(self):
        """Test add_accesslist alone does not surface the button.

        The gate lives in render() because ObjectView resolves
        permissions_required against the access list itself.
        """
        self.add_permissions("netbox_acls.add_accesslist")

        self.assertEqual(AddRule.render(self.get_context(self.standard), self.standard), "")

    def test_the_button_follows_the_access_list_type(self):
        """Test an extended list offers the extended rule form only."""
        self.add_permissions("netbox_acls.add_aclextendedrule")

        html = AddRule.render(self.get_context(self.extended), self.extended)

        self.assertIn(reverse("plugins:netbox_acls:aclextendedrule_add"), html)
        self.assertNotIn(reverse("plugins:netbox_acls:aclstandardrule_add"), html)
