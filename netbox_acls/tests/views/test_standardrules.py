from django.contrib.contenttypes.models import ContentType

from ipam.models import Prefix
from utilities.testing import create_tags

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLStandardRule
from .base import ACLRuleSequenceTestsMixin, PluginTestCases, build_ipam_objects


class ACLStandardRuleViewTestCase(ACLRuleSequenceTestsMixin, PluginTestCases.ObjectViewTestCase):
    """View tests for ACLStandardRule."""

    model = ACLStandardRule
    add_permission = "netbox_acls.add_aclstandardrule"
    change_permission = "netbox_acls.change_aclstandardrule"
    user_permissions = (
        "ipam.view_aggregate",
        "ipam.view_ipaddress",
        "ipam.view_iprange",
        "ipam.view_prefix",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        aggregate, cls.prefix, ip_address, ip_range = build_ipam_objects()

        cls.access_list = AccessList.objects.create(
            name="teststandardacl",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # create() not bulk_create(): save() populates the _source_* columns.
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=cls.prefix,
            description="permit the prefix",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=20,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=ip_address,
            description="deny the address",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=30,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=ip_range,
            description="deny the range",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=40,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="a standard remark",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=50,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=aggregate,
            description="deny the aggregate",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "access_list": cls.access_list.pk,
            "sequence": 60,
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "remark": "",
            "source_type": ContentType.objects.get_for_model(Prefix).pk,
            "source": cls.prefix.pk,
            "log_matches": True,
            "log_options": [ACLRuleLogOptionChoices.OPTION_SYSLOG],
            "description": "A new standard rule",
            "comments": "",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "Bulk edited",
        }

    def test_detail_view_renders_log_option_labels(self):
        """Test that the detail page shows option labels rather than stored values."""
        rule = ACLStandardRule.objects.create(
            access_list=self.access_list,
            sequence=200,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix,
            log_matches=True,
            log_options=[
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
                ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
            ],
        )
        self.add_permissions("netbox_acls.view_aclstandardrule")

        response = self.client.get(rule.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Syslog")
        self.assertContains(response, "Log-input")
        self.assertContains(response, 'class="badge text-bg-blue"')
        self.assertContains(response, 'class="badge text-bg-purple"')

    def test_bulk_edit_clears_options_while_logging_stays_enabled(self):
        """Test that options can be cleared without also disabling logging."""
        rules = [
            ACLStandardRule.objects.create(
                access_list=self.access_list,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=self.prefix,
                log_matches=True,
                log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
            )
            for sequence in (210, 220)
        ]
        self.add_permissions("netbox_acls.change_aclstandardrule", "netbox_acls.view_aclstandardrule")

        response = self.client.post(
            self._get_url("bulk_edit"),
            {
                "pk": [rule.pk for rule in rules],
                "_apply": True,
                "clear_log_options": True,
            },
        )
        self.assertHttpStatus(response, 302)

        for rule in rules:
            rule.refresh_from_db()
            self.assertTrue(rule.log_matches)
            self.assertEqual(rule.log_options, [])

    def test_bulk_edit_cannot_enable_logging_on_a_remark(self):
        """Test that the model's remark guard survives the bulk edit path."""
        rule = ACLStandardRule.objects.create(
            access_list=self.access_list,
            sequence=230,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="Remark",
        )
        self.add_permissions(
            "netbox_acls.change_aclstandardrule",
            "netbox_acls.view_aclstandardrule",
        )

        response = self.client.post(
            self._get_url("bulk_edit"),
            {
                "pk": [rule.pk],
                "_apply": True,
                "log_matches": "True",
            },
        )
        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Log matches must not be enabled")

        rule.refresh_from_db()
        self.assertFalse(rule.log_matches)
