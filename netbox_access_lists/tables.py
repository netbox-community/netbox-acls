"""
Define the object lists / table view for each of the plugin models.
"""

import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from .models import AccessList, ACLExtendedRule, ACLStandardRule

__all__ = (
    'AccessListTable',
    'ACLStandardRuleTable',
    'ACLExtendedRuleTable',
)


class AccessListTable(NetBoxTable):
    """
    Defines the table view for the AccessList model.
    """
    pk = columns.ToggleColumn()
    id = tables.Column(  # Provides a link to the secret
        linkify=True
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name='Assigned Host'
    )
    name = tables.Column(
        linkify=True
    )
    device = tables.Column(
        linkify=True
    )
    type = ChoiceFieldColumn()
    default_action = ChoiceFieldColumn()
    rule_count = tables.Column(
        verbose_name='Rule Count'
    )
    tags = columns.TagColumn(
        url_name='plugins:netbox_access_lists:accesslist_list'
    )

    class Meta(NetBoxTable.Meta):
        model = AccessList
        fields = ('pk', 'id', 'name', 'assigned_object', 'type', 'rule_count', 'default_action', 'comments', 'actions', 'tags')
        default_columns = ('name', 'assigned_object', 'type', 'rule_count', 'default_action', 'tags')


class ACLStandardRuleTable(NetBoxTable):
    """
    Defines the table view for the ACLStandardRule model.
    """
    access_list = tables.Column(
        linkify=True
    )
    index = tables.Column(
        linkify=True
    )
    action = ChoiceFieldColumn()
    tags = columns.TagColumn(
        url_name='plugins:netbox_access_lists:aclstandardrule_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ACLStandardRule
        fields = (
            'pk', 'id', 'access_list', 'index', 'action', 'actions', 'remark', 'tags', 'description',
        )
        default_columns = (
            'access_list', 'index', 'action', 'actions', 'remark', 'tags'
        )


class ACLExtendedRuleTable(NetBoxTable):
    """
    Defines the table view for the ACLExtendedRule model.
    """
    access_list = tables.Column(
        linkify=True
    )
    index = tables.Column(
        linkify=True
    )
    action = ChoiceFieldColumn()
    tags = columns.TagColumn(
        url_name='plugins:netbox_access_lists:aclextendedrule_list'
    )
    protocol = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = ACLExtendedRule
        fields = (
            'pk', 'id', 'access_list', 'index', 'action', 'actions', 'remark', 'tags', 'description',
            'source_prefix', 'source_ports', 'destination_prefix', 'destination_ports', 'protocol'
        )
        default_columns = (
            'access_list', 'index', 'action', 'actions', 'remark', 'tags',
            'source_prefix', 'source_ports', 'destination_prefix', 'destination_ports', 'protocol'
        )
