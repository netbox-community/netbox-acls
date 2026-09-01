"""Row-order tests for the declarative UI panels.

Each panel renders its attributes in declaration order, so these pin
the order the retired detail templates authored, except where an
accepted delta deliberately changed it.
"""

from django.test import SimpleTestCase

from ...ui.panels import (
    AccessListPanel,
    ACLAssignmentPanel,
    ACLExtendedRuleDetailsPanel,
    ACLExtendedRulePanel,
    ACLRuleLoggingPanel,
    ACLStandardRuleDetailsPanel,
    ACLStandardRulePanel,
)

EXPECTED_ORDER = {
    AccessListPanel: ["type", "family", "default_action", "rules", "description"],
    ACLAssignmentPanel: ["access_list", "assigned_object", "direction"],
    ACLStandardRulePanel: ["access_list", "sequence", "description"],
    # The extended template ordered these access list, description, sequence.
    ACLExtendedRulePanel: ["access_list", "sequence", "description"],
    ACLStandardRuleDetailsPanel: [
        "action",
        "remark",
        "source",
    ],
    ACLExtendedRuleDetailsPanel: [
        "action",
        "remark",
        "protocol",
        "source",
        "source_port_ranges",
        "destination",
        "destination_port_ranges",
    ],
    ACLRuleLoggingPanel: ["log_matches", "log_options"],
}


class PanelAttributeOrderTestCase(SimpleTestCase):
    """Pin the attribute order of every panel."""

    def test_panels_declare_attributes_in_the_authored_order(self):
        """Test each panel keeps the row order of the template it replaced."""
        for panel_class, expected in EXPECTED_ORDER.items():
            with self.subTest(panel=panel_class.__name__):
                self.assertEqual(list(panel_class._attrs), expected)
