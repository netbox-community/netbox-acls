from django.contrib.contenttypes.models import ContentType
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import override_settings
from netaddr import IPNetwork

from ipam.models import Prefix
from utilities.testing import ViewTestCases, create_tags

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTCPFlagChoices,
    ACLTCPFlagMatchChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLExtendedRule
from ...utils import normalize_port_ranges
from .base import ACLRuleSequenceTestsMixin, PluginViewTestCase, build_ipam_objects


@override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
class ACLExtendedRuleViewTestCase(
    ACLRuleSequenceTestsMixin,
    PluginViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):
    """View tests for ACLExtendedRule."""

    model = ACLExtendedRule
    add_permission = "netbox_acls.add_aclextendedrule"
    change_permission = "netbox_acls.change_aclextendedrule"
    user_permissions = (
        "ipam.view_aggregate",
        "ipam.view_ipaddress",
        "ipam.view_iprange",
        "ipam.view_prefix",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        aggregate, cls.source_prefix, ip_address, ip_range = build_ipam_objects()
        cls.destination_prefix = Prefix.objects.create(prefix=IPNetwork("10.2.0.0/16"))

        cls.access_list = AccessList.objects.create(
            name="testextendedacl",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # Stored half-open, so an inclusive 80 to 80 becomes [80, 81).
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            source=cls.source_prefix,
            destination=cls.destination_prefix,
            source_port_ranges=normalize_port_ranges([NumericRange(1024, 2048, bounds="[]")]),
            destination_port_ranges=normalize_port_ranges([NumericRange(80, 80, bounds="[]")]),
            description="permit web",
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=20,
            action=ACLRuleActionChoices.ACTION_DENY,
            protocol=ACLProtocolChoices.PROTOCOL_UDP,
            source=ip_address,
            destination=ip_range,
            destination_port_ranges=normalize_port_ranges([NumericRange(53, 53, bounds="[]")]),
            description="deny dns",
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=30,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            source=aggregate,
            destination=ip_address,
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=40,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="an extended remark",
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=50,
            action=ACLRuleActionChoices.ACTION_DENY,
            protocol=ACLProtocolChoices.PROTOCOL_IP,
            source=ip_range,
            destination=aggregate,
            description="deny the range",
        )

        cls.rules = list(ACLExtendedRule.objects.order_by("sequence"))

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # Ports are posted inclusively and need protocol tcp or udp. These values
        # round-trip unchanged: no single ports, no adjacent pairs to merge.
        cls.form_data = {
            "access_list": cls.access_list.pk,
            "sequence": 60,
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "remark": "",
            "protocol": ACLProtocolChoices.PROTOCOL_TCP,
            "tcp_flags": [ACLTCPFlagChoices.FLAG_RST, ACLTCPFlagChoices.FLAG_ACK],
            "tcp_flags_match": ACLTCPFlagMatchChoices.MATCH_ANY,
            "source_content_type": ContentType.objects.get_for_model(Prefix).pk,
            "source_object_id": cls.source_prefix.pk,
            "source_port_ranges": "1024-2048",
            "destination_content_type": ContentType.objects.get_for_model(Prefix).pk,
            "destination_object_id": cls.destination_prefix.pk,
            "destination_port_ranges": "8080-8081",
            "log_matches": True,
            "log_options": [ACLRuleLogOptionChoices.OPTION_SYSLOG],
            "description": "A new extended rule",
            "comments": "",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "Bulk edited",
            "tcp_flags_match": ACLTCPFlagMatchChoices.MATCH_ANY,
        }

        # Fourteen columns, so every row carries thirteen separators. Ports need tcp or udp.
        cls.csv_data = (
            (
                "access_list,sequence,action,protocol,source_type,source,source_port_ranges,"
                "destination_type,destination,destination_port_ranges,icmp_type,icmp_code,tcp_flags,tcp_flags_match"
            ),
            (
                f"{cls.access_list.name},210,permit,tcp,ipam.prefix,{cls.source_prefix.prefix},1024-2048,"
                f'ipam.prefix,{cls.destination_prefix.prefix},80-81,,,"ack,rst",any'
            ),
            (
                f"{cls.access_list.name},220,deny,udp,ipam.prefix,{cls.source_prefix.prefix},53,"
                f"ipam.prefix,{cls.destination_prefix.prefix},,,,,all"
            ),
            f"{cls.access_list.name},230,permit,ip,,,,,,,,,,all",
            f"{cls.access_list.name},240,permit,icmp,,,,,,,0,0,,all",
        )

        cls.csv_update_data = (
            "id,description",
            f"{cls.rules[0].pk},Updated by import",
            f"{cls.rules[1].pk},Updated by import too",
        )

    def test_detail_view_renders_log_option_labels(self):
        """Test that the detail page shows option labels rather than stored values."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list,
            sequence=200,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.source_prefix,
            log_matches=True,
            log_options=[
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
                ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
            ],
        )
        self.add_permissions("netbox_acls.view_aclextendedrule")

        response = self.client.get(rule.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Syslog")
        self.assertContains(response, "Log-input")
        self.assertContains(response, 'class="badge text-bg-blue"')
        self.assertContains(response, 'class="badge text-bg-purple"')

    def test_bulk_edit_clears_options_while_logging_stays_enabled(self):
        """Test that options can be cleared without also disabling logging."""
        rules = [
            ACLExtendedRule.objects.create(
                access_list=self.access_list,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=self.source_prefix,
                log_matches=True,
                log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
            )
            for sequence in (210, 220)
        ]
        self.add_permissions("netbox_acls.change_aclextendedrule", "netbox_acls.view_aclextendedrule")

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
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list,
            sequence=230,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="Remark",
        )
        self.add_permissions(
            "netbox_acls.change_aclextendedrule",
            "netbox_acls.view_aclextendedrule",
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

    def test_bulk_edit_clears_tcp_flags_while_the_match_stays(self):
        """Test that TCP flags can be cleared without also resetting the match."""
        rules = [
            ACLExtendedRule.objects.create(
                access_list=self.access_list,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=self.source_prefix,
                protocol=ACLProtocolChoices.PROTOCOL_TCP,
                tcp_flags=[ACLTCPFlagChoices.FLAG_ACK, ACLTCPFlagChoices.FLAG_RST],
                tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY,
            )
            for sequence in (240, 250)
        ]
        self.add_permissions("netbox_acls.change_aclextendedrule", "netbox_acls.view_aclextendedrule")

        response = self.client.post(
            self._get_url("bulk_edit"),
            {
                "pk": [rule.pk for rule in rules],
                "_apply": True,
                "clear_tcp_flags": True,
            },
        )
        self.assertHttpStatus(response, 302)

        for rule in rules:
            rule.refresh_from_db()
            self.assertEqual(rule.tcp_flags, [])
            self.assertEqual(rule.tcp_flags_match, ACLTCPFlagMatchChoices.MATCH_ANY)

    def test_bulk_edit_stores_an_icmp_type_of_zero(self):
        """Test that bulk edit stores an ICMP type of zero."""
        rules = [
            ACLExtendedRule.objects.create(
                access_list=self.access_list,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=self.source_prefix,
                protocol=ACLProtocolChoices.PROTOCOL_ICMP,
                icmp_type=8,
            )
            for sequence in (260, 270)
        ]
        self.add_permissions("netbox_acls.change_aclextendedrule", "netbox_acls.view_aclextendedrule")

        response = self.client.post(
            self._get_url("bulk_edit"),
            {
                "pk": [rule.pk for rule in rules],
                "_apply": True,
                "icmp_type": "0",
            },
        )
        self.assertHttpStatus(response, 302)

        for rule in rules:
            rule.refresh_from_db()
            self.assertEqual(rule.icmp_type, 0)

    def test_detail_view_renders_the_rule_attributes(self):
        """Test that the detail view renders the rule attributes."""
        self.add_permissions("netbox_acls.view_aclextendedrule")
        rule = ACLExtendedRule.objects.get(access_list=self.access_list, sequence=10)

        response = self.client.get(rule.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, rule.access_list.get_absolute_url())
        self.assertContains(response, rule.get_action_display())
        self.assertContains(response, rule.get_protocol_display())
        self.assertContains(response, rule.source.get_absolute_url())
        self.assertContains(response, rule.destination.get_absolute_url())
        # "1024-2048" is distinctive, unlike the destination's bare "80".
        self.assertContains(response, ", ".join(rule.source_port_ranges_list))

    def test_detail_view_renders_the_panel_attributes(self):
        """Test that the detail view renders the panel's own attribute anchors."""
        self.add_permissions("netbox_acls.view_aclextendedrule")
        rule = ACLExtendedRule.objects.get(access_list=self.access_list, sequence=10)

        response = self.client.get(rule.get_absolute_url())

        self.assertHttpStatus(response, 200)
        for anchor in (
            "sequence",
            "description",
            "source",
            "source_port_ranges",
            "destination",
            "destination_port_ranges",
        ):
            with self.subTest(attribute=anchor):
                self.assertContains(response, f'id="attr_{anchor}"')

    def test_add_form_shows_the_ports_for_tcp(self):
        """Test that an add form redrawn for TCP offers both port fields."""
        form = self._get_form(
            "add",
            self.add_permission,
            query=f"?action={ACLRuleActionChoices.ACTION_PERMIT}&protocol={ACLProtocolChoices.PROTOCOL_TCP}",
        )
        self.assertIn("source_port_ranges", form.fields)
        self.assertIn("destination_port_ranges", form.fields)

    def test_add_form_hides_the_criteria_until_an_action_is_picked(self):
        """Test that an add form opened without an action offers no match criteria."""
        form = self._get_form("add", self.add_permission)
        for field_name in (
            "source",
            "source_port_ranges",
            "destination",
            "destination_port_ranges",
            "protocol",
            "icmp_type",
            "icmp_code",
            "tcp_flags",
            "tcp_flags_match",
            "log_matches",
            "log_options",
        ):
            with self.subTest(field_name=field_name):
                self.assertNotIn(field_name, form.fields)
