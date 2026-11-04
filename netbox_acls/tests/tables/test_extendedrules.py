from django.db.models import Case, CharField, Value, When

from utilities.testing import TableTestCases

from ...choices import ACLRuleUsageChoices, ACLTCPFlagMatchChoices
from ...models import ACLExtendedRule
from ...tables import ACLExtendedRuleTable, ACLExtendedRuleUsageTable


class ACLExtendedRuleTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACLExtendedRuleTable

    def test_logging_columns_are_available_and_log_matches_is_default(self):
        """Test that both logging columns exist and only the master switch shows by default."""
        self.assertIn("log_matches", ACLExtendedRuleTable.base_columns)
        self.assertIn("log_options_list", ACLExtendedRuleTable.base_columns)
        self.assertIn("log_matches", ACLExtendedRuleTable.Meta.default_columns)
        self.assertNotIn("log_options_list", ACLExtendedRuleTable.Meta.default_columns)

    def test_log_options_column_renders_colored_badges(self):
        """Test that the column badges each option and exports the plain labels."""
        rule = ACLExtendedRule(log_options=["syslog", "cisco-log-input"])
        table = ACLExtendedRuleTable([rule])
        cell = table.rows[0].get_cell("log_options_list")
        self.assertInHTML('<span class="badge text-bg-blue">Syslog</span>', cell)
        self.assertInHTML(
            '<span class="badge text-bg-purple">Log-input</span>',
            cell,
        )
        self.assertEqual(
            table.rows[0].get_cell_value("log_options_list"),
            "Syslog, Log-input",
        )

    def test_icmp_and_tcp_flag_columns_are_available_but_not_default(self):
        """Test that the ICMP and TCP flag columns exist but none shows by default."""
        self.assertIn("icmp_type", ACLExtendedRuleTable.base_columns)
        self.assertIn("icmp_code", ACLExtendedRuleTable.base_columns)
        self.assertIn("tcp_flags_list", ACLExtendedRuleTable.base_columns)
        self.assertIn("tcp_flags_match", ACLExtendedRuleTable.base_columns)
        self.assertNotIn("icmp_type", ACLExtendedRuleTable.Meta.default_columns)
        self.assertNotIn("icmp_code", ACLExtendedRuleTable.Meta.default_columns)
        self.assertNotIn("tcp_flags_list", ACLExtendedRuleTable.Meta.default_columns)
        self.assertNotIn("tcp_flags_match", ACLExtendedRuleTable.Meta.default_columns)

    def test_tcp_flags_column_exports_the_labels(self):
        """Test that the TCP flags column exports the plain labels."""
        rule = ACLExtendedRule(tcp_flags=["ack", "rst"])
        table = ACLExtendedRuleTable([rule])
        self.assertEqual(
            table.rows[0].get_cell_value("tcp_flags_list"),
            "ACK, RST",
        )

    def test_tcp_flags_match_column_exports_the_stored_mode_without_flags(self):
        """Test that the match column exports the stored mode of a rule without flags."""
        expected = {
            ACLTCPFlagMatchChoices.MATCH_ALL: "All",
            ACLTCPFlagMatchChoices.MATCH_ANY: "Any",
        }
        for mode, label in expected.items():
            with self.subTest(tcp_flags_match=mode):
                rule = ACLExtendedRule(tcp_flags=[], tcp_flags_match=mode)
                table = ACLExtendedRuleTable([rule])
                self.assertEqual(table.rows[0].get_cell_value("tcp_flags_match"), label)

    def test_icmp_type_column_shows_zero(self):
        """Test that the ICMP type column shows a type of zero."""
        rule = ACLExtendedRule(icmp_type=0)
        table = ACLExtendedRuleTable([rule])
        self.assertEqual(str(table.rows[0].get_cell("icmp_type")), "0")


class ACLExtendedRuleUsageTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACLExtendedRuleUsageTable

    @classmethod
    def get_queryset_sources(cls):
        """The usage table is fed by a children view, which the default discovery skips."""
        return (
            (
                "ACLExtendedRuleChildrenView",
                ACLExtendedRule.objects.annotate(
                    used_as=Case(
                        When(destination_id__isnull=False, then=Value(ACLRuleUsageChoices.USAGE_BOTH)),
                        default=Value(ACLRuleUsageChoices.USAGE_SOURCE),
                        output_field=CharField(),
                    ),
                ),
            ),
        )

    def test_usage_column_is_available_and_shown_by_default(self):
        """Test that the usage column is declared and visible without configuration."""
        self.assertIn("used_as", ACLExtendedRuleUsageTable.base_columns)
        self.assertIn("used_as", ACLExtendedRuleUsageTable.Meta.fields)
        self.assertIn("used_as", ACLExtendedRuleUsageTable.Meta.default_columns)

    def test_usage_column_renders_a_colored_badge_per_role(self):
        """Test that each usage role renders its own label and color."""
        expected = {
            ACLRuleUsageChoices.USAGE_SOURCE: ("Source", "blue"),
            ACLRuleUsageChoices.USAGE_DESTINATION: ("Destination", "purple"),
            ACLRuleUsageChoices.USAGE_BOTH: ("Source and destination", "teal"),
        }
        for value, (label, color) in expected.items():
            with self.subTest(used_as=value):
                rule = ACLExtendedRule()
                rule.used_as = value
                table = ACLExtendedRuleUsageTable([rule])
                self.assertInHTML(
                    f'<span class="badge text-bg-{color}">{label}</span>',
                    table.rows[0].get_cell("used_as"),
                )

    def test_usage_column_value_hook_yields_the_label(self):
        """Test that the column's value hook yields the label rather than the stored token."""
        rule = ACLExtendedRule()
        rule.used_as = ACLRuleUsageChoices.USAGE_BOTH
        table = ACLExtendedRuleUsageTable([rule])
        self.assertEqual(table.rows[0].get_cell_value("used_as"), "Source and destination")
