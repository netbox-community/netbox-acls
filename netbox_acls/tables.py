"""
Define the object lists / table view for each of the plugin models.
"""

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from .models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule

__all__ = (
    "AccessListTable",
    "ACLAssignmentTable",
    "ACLStandardRuleTable",
    "ACLExtendedRuleTable",
)


class AccessListTable(NetBoxTable):
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
    device = tables.Column(
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

    class Meta(NetBoxTable.Meta):
        model = AccessList
        fields = (
            "pk",
            "id",
            "name",
            "type",
            "family",
            "rule_count",
            "default_action",
            "comments",
            "action",
            "tags",
        )
        default_columns = (
            "name",
            "type",
            "family",
            "rule_count",
            "default_action",
            "tags",
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
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclassignment_list",
    )
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
            "tags",
        )
        default_columns = (
            "id",
            "access_list",
            "type",
            "family",
            "assigned_object",
            "direction",
            "tags",
        )


class ACLStandardRuleTable(NetBoxTable):
    """
    Defines the table view for the ACLStandardRule model.
    """

    access_list = tables.Column(
        linkify=True,
    )
    sequence = tables.Column(
        verbose_name=_("Seq"),
        linkify=True,
    )
    action = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclstandardrule_list",
    )

    # Source
    source_type = columns.ContentTypeColumn(
        verbose_name=_("Source Type"),
    )
    source = tables.Column(
        verbose_name=_("Source"),
        orderable=False,
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = ACLStandardRule
        fields = (
            "pk",
            "id",
            "access_list",
            "sequence",
            "action",
            "remark",
            "tags",
            "description",
            "source",
        )
        default_columns = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "source",
            "tags",
        )


class ACLExtendedRuleTable(NetBoxTable):
    """
    Defines the table view for the ACLExtendedRule model.
    """

    access_list = tables.Column(
        linkify=True,
    )
    sequence = tables.Column(
        verbose_name=_("Seq"),
        linkify=True,
    )
    action = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclextendedrule_list",
    )
    protocol = columns.ChoiceFieldColumn()

    # Source
    source_type = columns.ContentTypeColumn(
        verbose_name=_("Source Type"),
    )
    source = tables.Column(
        verbose_name=_("Source"),
        orderable=False,
        linkify=True,
    )
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

    class Meta(NetBoxTable.Meta):
        model = ACLExtendedRule
        fields = (
            "pk",
            "id",
            "access_list",
            "sequence",
            "action",
            "remark",
            "tags",
            "description",
            "source",
            "source_port_ranges_list",
            "destination",
            "destination_port_ranges_list",
            "protocol",
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
            "tags",
        )
