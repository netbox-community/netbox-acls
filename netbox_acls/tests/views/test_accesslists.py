from django.urls import reverse

from utilities.testing import create_tags

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLExtendedRule, ACLStandardRule
from ...tables import ACLExtendedRuleTable, ACLStandardRuleTable
from .base import PluginTestCases


class AccessListViewTestCase(PluginTestCases.ObjectViewTestCase):
    """View tests for AccessList."""

    model = AccessList

    @classmethod
    def setUpTestData(cls):
        AccessList.objects.bulk_create(
            (
                AccessList(
                    name="testacl1",
                    type=ACLTypeChoices.TYPE_STANDARD,
                    family=ACLFamilyChoices.FAMILY_IPV4,
                    default_action=ACLActionChoices.ACTION_DENY,
                ),
                AccessList(
                    name="testacl2",
                    type=ACLTypeChoices.TYPE_EXTENDED,
                    family=ACLFamilyChoices.FAMILY_IPV4,
                    default_action=ACLActionChoices.ACTION_PERMIT,
                ),
                AccessList(
                    name="testacl3",
                    type=ACLTypeChoices.TYPE_EXTENDED,
                    family=ACLFamilyChoices.FAMILY_IPV6,
                    default_action=ACLActionChoices.ACTION_DENY,
                ),
                # A second list of each type, so both branches of the rules table have
                # same-relation rules to exclude. Both sort after testacl4, which
                # form_data creates, so the name-ordered first() that the inherited view
                # tests act on stays testacl1.
                AccessList(
                    name="testacl5",
                    type=ACLTypeChoices.TYPE_STANDARD,
                    family=ACLFamilyChoices.FAMILY_IPV4,
                    default_action=ACLActionChoices.ACTION_DENY,
                ),
                AccessList(
                    name="testacl6",
                    type=ACLTypeChoices.TYPE_EXTENDED,
                    family=ACLFamilyChoices.FAMILY_IPV4,
                    default_action=ACLActionChoices.ACTION_DENY,
                ),
            ),
        )

        # create() not bulk_create(): save() populates the shadow source columns.
        standard, other_standard = (
            AccessList.objects.get(name="testacl1"),
            AccessList.objects.get(name="testacl5"),
        )
        extended = AccessList.objects.get(name="testacl2")
        cls.standard_rules = [
            ACLStandardRule.objects.create(
                access_list=standard,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_REMARK,
                remark=f"standard remark {sequence}",
            )
            for sequence in (10, 20)
        ]
        cls.extended_rules = [
            ACLExtendedRule.objects.create(
                access_list=extended,
                sequence=10,
                action=ACLRuleActionChoices.ACTION_REMARK,
                remark="extended remark 10",
            ),
        ]
        ACLStandardRule.objects.create(
            access_list=other_standard,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="a rule on another standard list",
        )
        ACLExtendedRule.objects.create(
            access_list=AccessList.objects.get(name="testacl6"),
            sequence=10,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="a rule on another extended list",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "testacl4",
            "type": ACLTypeChoices.TYPE_STANDARD,
            "family": ACLFamilyChoices.FAMILY_IPV4,
            "default_action": ACLActionChoices.ACTION_DENY,
            "description": "A new access list",
            "comments": "",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "Bulk edited",
        }

    def test_rules_table_matches_access_list_type(self):
        """Test that the detail view renders the rule table matching the ACL's type."""
        self.add_permissions("netbox_acls.view_accesslist")

        for name, table_class, expected_rules in (
            ("testacl1", ACLStandardRuleTable, self.standard_rules),
            ("testacl2", ACLExtendedRuleTable, self.extended_rules),
        ):
            with self.subTest(access_list=name):
                access_list = AccessList.objects.get(name=name)
                response = self.client.get(access_list.get_absolute_url())
                self.assertHttpStatus(response, 200)

                table = response.context["rules_table"]
                self.assertIsInstance(table, table_class)
                # Scoped to this list, not every rule of that type.
                self.assertEqual(
                    {rule.pk for rule in table.data},
                    {rule.pk for rule in expected_rules},
                )
                # The column is redundant on an access list's own detail page.
                visible = [column.name for column in table.columns.itervisible()]
                self.assertNotIn("access_list", visible)
                # The embedded table is the page's subject, so it shows the full logging state.
                self.assertIn("log_matches", visible)
                self.assertIn("log_options_list", visible)

    def test_detail_view_renders_the_access_list_attributes(self):
        """Test that the detail view renders the access list attributes."""
        self.add_permissions("netbox_acls.view_accesslist")
        access_list = AccessList.objects.get(name="testacl1")
        rule_list_url = reverse("plugins:netbox_acls:aclstandardrule_list")

        response = self.client.get(access_list.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, access_list.get_type_display())
        self.assertContains(response, access_list.get_family_display())
        self.assertContains(response, access_list.get_default_action_display())
        self.assertContains(response, f"{rule_list_url}?access_list_id={access_list.pk}")

    def test_detail_view_renders_the_panel_attributes(self):
        """Test that the detail view renders the panel's own attribute anchors."""
        self.add_permissions("netbox_acls.view_accesslist")
        access_list = AccessList.objects.get(name="testacl1")

        response = self.client.get(access_list.get_absolute_url())

        self.assertHttpStatus(response, 200)
        # Only text, numeric, array and generic foreign key attributes emit an
        # anchor. Choice and related object attributes are pinned by _attrs order.
        self.assertContains(response, 'id="attr_rules"')
