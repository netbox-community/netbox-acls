import html
import re

from django.urls import reverse

from utilities.testing import create_tags

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLExtendedRule, ACLStandardRule
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
                # A second list of each type, carrying rules the embedded table must
                # exclude. Both sort after testacl4, which form_data creates, so the
                # name-ordered first() the inherited view tests act on stays testacl1.
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
        """Test that the embedded rule table holds this ACL's rules and no others."""
        self.add_permissions(
            "netbox_acls.view_accesslist",
            "netbox_acls.view_aclstandardrule",
            "netbox_acls.view_aclextendedrule",
        )
        standard_url = reverse("plugins:netbox_acls:aclstandardrule_list")
        extended_url = reverse("plugins:netbox_acls:aclextendedrule_list")

        for name, list_url, expected_rules in (
            ("testacl1", standard_url, self.standard_rules),
            ("testacl2", extended_url, self.extended_rules),
        ):
            with self.subTest(access_list=name):
                access_list = AccessList.objects.get(name=name)

                response = self.client.get(access_list.get_absolute_url())

                self.assertHttpStatus(response, 200)
                content = response.content.decode()
                self.assertIn("exclude_columns=access_list", content)
                self.assertIn("include_columns=log_matches%2Clog_options_list", content)

                # Exactly one rules card renders, for the matching model. Other
                # hx-get URLs on the page belong to core, such as notifications.
                embeds = [
                    html.unescape(url)
                    for url in re.findall(r'hx-get="([^"]+)"', content)
                    if url.startswith((standard_url, extended_url))
                ]
                self.assertEqual(len(embeds), 1, embeds)
                embed_url = embeds[0]
                self.assertTrue(embed_url.startswith(list_url), embed_url)

                # Follow it, or nothing pins which rows the card actually lists.
                embedded = self.client.get(embed_url, headers={"hx-request": "true"})

                self.assertHttpStatus(embedded, 200)
                self.assertEqual(
                    {rule.pk for rule in embedded.context["table"].data},
                    {rule.pk for rule in expected_rules},
                )

    def test_detail_view_renders_the_access_list_attributes(self):
        """Test that the detail view renders the access list attributes."""
        self.add_permissions("netbox_acls.view_accesslist")
        access_list = AccessList.objects.get(name="testacl1")
        rule_list_url = reverse("plugins:netbox_acls:aclstandardrule_list")

        response = self.client.get(access_list.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertInHTML(
            f'<span class="badge text-bg-{access_list.get_type_color()}">{access_list.get_type_display()}</span>',
            response.content.decode(),
        )
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
