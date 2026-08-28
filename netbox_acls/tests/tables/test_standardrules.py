from ...models import ACLStandardRule
from ...tables import ACLStandardRuleTable
from . import base


class ACLStandardRuleTableTestCase(base.StandardTableTestCase):
    table = ACLStandardRuleTable

    def test_logging_columns_are_available_and_log_matches_is_default(self):
        """Test that both logging columns exist and only the master switch shows by default."""
        self.assertIn("log_matches", ACLStandardRuleTable.base_columns)
        self.assertIn("log_options_list", ACLStandardRuleTable.base_columns)
        self.assertIn("log_matches", ACLStandardRuleTable.Meta.default_columns)
        self.assertNotIn("log_options_list", ACLStandardRuleTable.Meta.default_columns)

    def test_log_options_column_renders_colored_badges(self):
        """Test that the column badges each option and exports the plain labels."""
        rule = ACLStandardRule(log_options=["syslog", "cisco-log-input"])
        table = ACLStandardRuleTable([rule])
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
