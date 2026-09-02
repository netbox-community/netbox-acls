"""Unit tests for the plugin's detail view panels."""

from django.test import SimpleTestCase
from django.urls import reverse

from netbox.ui.actions import AddObject
from utilities.views import get_view

from ...choices import ACLTypeChoices
from ...models import AccessList, ACLExtendedRule, ACLStandardRule
from ...ui.panels import RuleTablePanel
from .base import UITestCase


class RuleTablePanelTestCase(UITestCase):
    """Test the rule table panels on the access list detail view."""

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

    @staticmethod
    def _standard_panel():
        return RuleTablePanel(
            ACLTypeChoices.TYPE_STANDARD,
            "netbox_acls.aclstandardrule",
            "Standard Rules",
        )

    def _should_render(self, panel, access_list):
        return panel.should_render(panel.get_context(self.get_context(access_list)))

    def test_the_panel_renders_on_a_matching_access_list(self):
        """Test a standard access list shows the standard rules panel."""
        self.add_permissions("netbox_acls.view_aclstandardrule")

        self.assertTrue(self._should_render(self._standard_panel(), self.standard))

    def test_the_panel_is_hidden_on_a_mismatched_access_list(self):
        """Test an extended access list hides the standard rules panel."""
        self.add_permissions("netbox_acls.view_aclstandardrule")

        self.assertFalse(self._should_render(self._standard_panel(), self.extended))

    def test_the_panel_is_hidden_without_the_rule_view_permission(self):
        """Test the card disappears for a user who may not view the rules.

        The retired template built its table from an unrestricted
        queryset and had no such gate.
        """
        self.assertFalse(self._should_render(self._standard_panel(), self.standard))

    def test_the_add_rule_button_links_to_a_prefilled_form(self):
        """Test the card's Add Rule button opens the rule form for this list."""
        action = next(a for a in self._standard_panel().actions if isinstance(a, AddObject))

        url = action.get_url(self.get_context(self.standard))

        self.assertTrue(url.startswith(reverse("plugins:netbox_acls:aclstandardrule_add")))
        self.assertIn(f"access_list={self.standard.pk}", url)
        self.assertIn("return_url=", url)


class RuleTablePanelDeclarationTestCase(SimpleTestCase):
    """Test how the access list detail view declares its rule table panels."""

    @staticmethod
    def _rule_panels():
        """Yield every rule table panel the access list layout declares."""
        layout = get_view(AccessList).layout
        return [panel for row in layout for column in row for panel in column if isinstance(panel, RuleTablePanel)]

    def test_every_access_list_type_has_a_rules_panel(self):
        """Test no access list type is left without a rules table."""
        self.assertEqual(
            sorted(panel.acl_type for panel in self._rule_panels()),
            sorted(ACLTypeChoices.values()),
        )

    def test_each_panel_lists_the_rule_model_for_its_type(self):
        """Test each panel lists the rule model matching its own type."""
        expected = {
            ACLTypeChoices.TYPE_STANDARD: ACLStandardRule,
            ACLTypeChoices.TYPE_EXTENDED: ACLExtendedRule,
        }
        for panel in self._rule_panels():
            with self.subTest(type=panel.acl_type):
                self.assertEqual(panel.model, expected[panel.acl_type])

    def test_each_panel_offers_a_prefilled_add_rule_action(self):
        """Test every prefill key survives the rule form load.

        An unknown key is dropped when the form loads, so the field
        opens empty and nothing raises.
        """
        for panel in self._rule_panels():
            action = next(a for a in panel.actions if isinstance(a, AddObject))
            form = get_view(panel.model, "edit").form
            with self.subTest(model=panel.model.__name__):
                self.assertEqual(action.model, panel.model)
                self.assertEqual(set(action.url_params), {"access_list"})
                for key in action.url_params:
                    self.assertIn(key, form.base_fields)
