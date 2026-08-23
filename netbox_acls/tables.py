"""
Define the object lists / table view for each of the plugin models.
"""

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, PrimaryModelTable, columns

from .models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule


class LogOptionsColumn(columns.TemplateColumn):
    """
    Display each log option as a colored badge.
    """

    template_code = """
    {% for label, color in record.log_options_badges %}
      {% badge label bg_color=color %}
    {% empty %}
      {{ ''|placeholder }}
    {% endfor %}
    """

    def __init__(self, **kwargs):
        super().__init__(template_code=self.template_code, orderable=False, **kwargs)

    def value(self, value):
        """Export the labels rather than the rendered badges."""
        return ", ".join(value)


__all__ = (
    "ACLAssignmentTable",
    "ACLExtendedRuleTable",
    "ACLStandardRuleTable",
    "AccessListTable",
)


class AccessListTable(PrimaryModelTable):
    """
    Defines the table view for the AccessList model.
    """

    pk = columns.ToggleColumn()
    id = tables.Column(
        linkify=True,
    )
    name = tables.Column(
        linkify=True,
    )
    type = columns.ChoiceFieldColumn()
    family = columns.ChoiceFieldColumn()
    default_action = columns.ChoiceFieldColumn()
    rule_count = tables.Column(
        verbose_name=_("Rule Count"),
    )
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:accesslist_list",
    )

    class Meta(PrimaryModelTable.Meta):
        model = AccessList
        fields = (
            "pk",
            "id",
            "name",
            "type",
            "family",
            "rule_count",
            "default_action",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "name",
            "type",
            "family",
            "rule_count",
            "default_action",
            "description",
        )


class ACLAssignmentTable(NetBoxTable):
    """
    Defines the table view for the AccessList model.
    """

    pk = columns.ToggleColumn()
    id = tables.Column(
        linkify=True,
    )
    access_list = tables.Column(
        linkify=True,
    )
    family = columns.ChoiceFieldColumn()
    assigned_object_type = columns.ContentTypeColumn(
        linkify=True,
    )
    assigned_object = tables.Column(
        verbose_name=_("Assigned Object"),
        orderable=False,
        linkify=True,
    )
    direction = columns.ChoiceFieldColumn()
    type = tables.Column(
        accessor=tables.A("access_list__type"),
        orderable=False,
        verbose_name=_("Type"),
    )
    default_action = tables.Column(
        accessor=tables.A("access_list__default_action"),
        orderable=False,
        verbose_name=_("Default Action"),
    )
    owner_group = tables.Column(
        accessor="owner__group",
        linkify=True,
        verbose_name=_("Owner Group"),
    )
    owner = tables.Column(
        linkify=True,
        verbose_name=_("Owner"),
    )
    comments = columns.MarkdownColumn(
        verbose_name=_("Comments"),
    )
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclassignment_list",
    )

    class Meta(NetBoxTable.Meta):
        model = ACLAssignment
        fields = (
            "pk",
            "id",
            "access_list",
            "family",
            "assigned_object_type",
            "assigned_object",
            "direction",
            "owner",
            "tags",
        )
        default_columns = (
            "id",
            "access_list",
            "type",
            "family",
            "assigned_object",
            "direction",
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
