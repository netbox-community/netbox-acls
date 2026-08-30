"""
Define the table views for the access list rule models.
"""

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import PrimaryModelTable, columns

from ..models import ACLExtendedRule, ACLStandardRule
from .columns import LogOptionsColumn, UsedAsColumn

__all__ = (
    "ACLExtendedRuleTable",
    "ACLExtendedRuleUsageTable",
    "ACLRuleTable",
    "ACLStandardRuleTable",
)


class ACLRuleTable(PrimaryModelTable):
    """
    Abstract table for all ACL rules.
    """

    access_list = tables.Column(
        linkify=True,
    )
    sequence = tables.Column(
        verbose_name=_("Seq"),
        linkify=True,
    )
    action = columns.ChoiceFieldColumn()

    # Source
    source_type = columns.ContentTypeColumn(
        verbose_name=_("Source Type"),
    )
    source = tables.Column(
        verbose_name=_("Source"),
        orderable=False,
        linkify=True,
    )

    # Logging
    log_matches = columns.BooleanColumn(
        verbose_name=_("Log Matches"),
    )
    log_options_list = LogOptionsColumn(
        verbose_name=_("Log Options"),
    )

    class Meta(PrimaryModelTable.Meta):
        fields = (
            "pk",
            "id",
            "access_list",
            "sequence",
            "action",
            "remark",
            "source",
            "source_type",
            "log_matches",
            "log_options_list",
            "description",
            "tags",
            "comments",
        )
        default_columns = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "source",
            "log_matches",
        )


class ACLStandardRuleTable(ACLRuleTable):
    """
    Defines the table view for the ACLStandardRule model.
    """

    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclstandardrule_list",
    )

    class Meta(ACLRuleTable.Meta):
        model = ACLStandardRule


class ACLExtendedRuleTable(ACLRuleTable):
    """
    Defines the table view for the ACLExtendedRule model.
    """

    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclextendedrule_list",
    )
    protocol = columns.ChoiceFieldColumn()

    # Source
    source_port_ranges_list = columns.ArrayColumn(
        verbose_name=_("Source Ports"),
        orderable=False,
    )

    # Destination
    destination_type = columns.ContentTypeColumn(
        verbose_name=_("Destination Type"),
    )
    destination = tables.Column(
        verbose_name=_("Destination"),
        orderable=False,
        linkify=True,
    )
    destination_port_ranges_list = columns.ArrayColumn(
        verbose_name=_("Destination Ports"),
        orderable=False,
    )

    class Meta(ACLRuleTable.Meta):
        model = ACLExtendedRule
        fields = ACLRuleTable.Meta.fields + (
            "protocol",
            "source_port_ranges_list",
            "destination",
            "destination_type",
            "destination_port_ranges_list",
        )
        default_columns = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "protocol",
            "source",
            "source_port_ranges_list",
            "destination",
            "destination_port_ranges_list",
            "log_matches",
        )


class ACLExtendedRuleUsageTable(ACLExtendedRuleTable):
    """
    Defines the table view for extended rules listed against a referenced object.
    """

    used_as = UsedAsColumn(
        verbose_name=_("Used As"),
    )

    class Meta(ACLExtendedRuleTable.Meta):
        fields = ACLExtendedRuleTable.Meta.fields + ("used_as",)
        default_columns = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "used_as",
            "protocol",
            "source",
            "source_port_ranges_list",
            "destination",
            "destination_port_ranges_list",
            "log_matches",
        )
