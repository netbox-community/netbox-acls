import django_tables2 as tables

from netbox.tables import NetBoxTable, columns, ChoiceFieldColumn
from .models import AccessList, AccessListRule


class AccessListTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    device = tables.Column(
        linkify=True
    )
    type = ChoiceFieldColumn()
    default_action = ChoiceFieldColumn()
    rule_count = tables.Column()
    tags = columns.TagColumn(
        url_name='plugins:netbox_access_lists:accesslist_list'
    )

    class Meta(NetBoxTable.Meta):
        model = AccessList
        fields = ('pk', 'id', 'name', 'device', 'type', 'rule_count', 'default_action', 'comments', 'actions', 'tags')
        default_columns = ('name', 'device', 'type', 'rule_count', 'default_action', 'tags')


class AccessListRuleTable(NetBoxTable):
    access_list = tables.Column(
        linkify=True
    )
    index = tables.Column(
        linkify=True
    )
    protocol = ChoiceFieldColumn()
    action = ChoiceFieldColumn()
    tags = columns.TagColumn(
        url_name='plugins:netbox_access_lists:accesslistrule_list'
    )

    class Meta(NetBoxTable.Meta):
        model = AccessListRule
        fields = (
            'pk', 'id', 'access_list', 'index', 'source_prefix', 'source_ports', 'destination_prefix',
            'destination_ports', 'protocol', 'action', 'remark', 'actions', 'tags'
        )
        default_columns = (
            'access_list', 'index', 'remark', 'source_prefix', 'source_ports', 'destination_prefix',
            'destination_ports', 'protocol', 'action', 'actions', 'tags'
        )
