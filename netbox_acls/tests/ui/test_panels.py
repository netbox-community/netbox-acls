"""Unit tests for the plugin's detail view panels."""

from django.test import SimpleTestCase
from django.urls import reverse

from netbox.ui.actions import AddObject
from utilities.views import get_view

from ...choices import ACLTypeChoices
from ...models import AccessList, ACLAddressGroup, ACLAddressGroupMember, ACLExtendedRule, ACLStandardRule
from ...ui.panels import MemberTablePanel, RuleTablePanel
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


class MemberTablePanelDeclarationTestCase(SimpleTestCase):
    @staticmethod
    def _member_panels():
        """Return every member table panel the address group layout declares."""
        layout = get_view(ACLAddressGroup).layout
        return [panel for row in layout for column in row for panel in column if isinstance(panel, MemberTablePanel)]

    def test_the_group_view_lists_only_its_own_members(self):
        """Test the group view lists only its own members."""
        panels = self._member_panels()

        self.assertEqual(len(panels), 1)
        panel = panels[0]
        self.assertEqual(panel.model, ACLAddressGroupMember)
        context = {"object": ACLAddressGroup(pk=7)}
        self.assertEqual({key: value(context) for key, value in panel.filters.items()}, {"address_group_id": 7})

    def test_the_add_member_action_prefills_the_group(self):
        """Test the Add Member action prefills the group."""
        panel = self._member_panels()[0]
        action = next(a for a in panel.actions if isinstance(a, AddObject))
        context = {"object": ACLAddressGroup(pk=7)}
        self.assertEqual(action.model, ACLAddressGroupMember)
        self.assertEqual({key: value(context) for key, value in action.url_params.items()}, {"address_group": 7})
        self.assertIn("address_group", get_view(ACLAddressGroupMember, "edit").form.base_fields)


class MemberTablePanelTestCase(UITestCase):
    """Test the member table panel on the address group detail view."""

    @classmethod
    def setUpTestData(cls):
        """Create an address group."""
        cls.group = ACLAddressGroup.objects.create(name="member-panel")

    def test_the_panel_renders_with_member_view_permission(self):
        """Test an empty group still offers its panel to a permitted user."""
        self.add_permissions("netbox_acls.view_acladdressgroupmember")
        panel = MemberTablePanel()

        self.assertTrue(panel.should_render(panel.get_context(self.get_context(self.group))))

    def test_the_panel_is_hidden_without_member_view_permission(self):
        """Test group-view permission does not grant membership-view permission."""
        self.add_permissions("netbox_acls.view_acladdressgroup")
        panel = MemberTablePanel()

        self.assertFalse(panel.should_render(panel.get_context(self.get_context(self.group))))
