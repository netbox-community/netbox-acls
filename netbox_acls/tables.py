"""
Define the object lists / table view for each of the plugin models.
"""

import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from .models import AccessList, ACLExtendedRule, ACLInterfaceAssignment, ACLStandardRule

__all__ = (
    "AccessListTable",
    "ACLInterfaceAssignmentTable",
    "ACLStandardRuleTable",
    "ACLExtendedRuleTable",
)


COL_HOST_ASSIGNMENT = """
    {% if record.assigned_object.device %}
    <a href="{{ record.assigned_object.device.get_absolute_url }}">{{ record.assigned_object.device|placeholder }}</a>
    {% else %}
    <a href="{{ record.assigned_object.virtual_machine.get_absolute_url }}">{{ record.assigned_object.virtual_machine|placeholder }}</a>
    {% endif %}
 """
COL_SOURCE_AND_DESTINATION_ASSIGNMENT = """
    {% if record.#replaceme#_prefix %}
        <a href="{{ record.#replaceme#_prefix.get_absolute_url }}">{{ record.#replaceme#_prefix|placeholder }}</a>
        <span class="badge text-bg-grey">Prefix</span>
    {% elif record.#replaceme#_iprange %}
        <a href="{{ record.#replaceme#_iprange.get_absolute_url }}">{{ record.#replaceme#_iprange|placeholder }}</a>
        <span class="badge text-bg-grey">IP-Range</span>
    {% elif record.#replaceme#_ipaddress %}
        <a href="{{ record.#replaceme#_ipaddress.get_absolute_url }}">{{ record.#replaceme#_ipaddress|placeholder }}</a>
        <span class="badge text-bg-grey">IP-Address</span>
    {% elif record.#replaceme#_aggregate %}
        <a href="{{ record.#replaceme#_aggregate.get_absolute_url }}">{{ record.#replaceme#_aggregate|placeholder }}</a>
        <span class="badge text-bg-grey">Aggregate</span>
    {% elif record.#replaceme#_service %}
        <a href="{{ record.#replaceme#_service.get_absolute_url }}">{{ record.#replaceme#_service|placeholder }}</a>
        <span class="badge text-bg-grey">Service</span>
    {% else %}
        {{ ''|placeholder }}
    {% endif %}
 """

class AccessListTable(NetBoxTable):
    """
    Defines the table view for the AccessList model.
    """

    pk = columns.ToggleColumn()
    id = tables.Column(
        linkify=True,
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name="Assigned Host",
    )
    name = tables.Column(
        linkify=True,
    )
    device = tables.Column(
        linkify=True,
    )
    type = ChoiceFieldColumn()
    default_action = ChoiceFieldColumn()
    rule_count = tables.Column(
        verbose_name="Rule Count",
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
            "assigned_object",
            "type",
            "rule_count",
            "default_action",
            "comments",
            "action",
            "tags",
        )
        default_columns = (
            "name",
            "assigned_object",
            "type",
            "rule_count",
            "default_action",
            "tags",
        )


class ACLInterfaceAssignmentTable(NetBoxTable):
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
    direction = ChoiceFieldColumn()
    host = tables.TemplateColumn(
        template_code=COL_HOST_ASSIGNMENT,
        orderable=False,
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name="Assigned Interface",
    )
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclinterfaceassignment_list",
    )

    class Meta(NetBoxTable.Meta):
        model = ACLInterfaceAssignment
        fields = (
            "pk",
            "id",
            "access_list",
            "direction",
            "host",
            "assigned_object",
            "tags",
        )
        default_columns = (
            "id",
            "access_list",
            "direction",
            "host",
            "assigned_object",
            "tags",
        )


class ACLStandardRuleTable(NetBoxTable):
    """
    Defines the table view for the ACLStandardRule model.
    """

    access_list = tables.Column(
        linkify=True,
    )
    index = tables.Column(
        linkify=True,
    )
    action = ChoiceFieldColumn()
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclstandardrule_list",
    )
    source = tables.TemplateColumn(
        template_code=COL_SOURCE_AND_DESTINATION_ASSIGNMENT.replace('#replaceme#', 'source'),
        order_by=('source_prefix', 'source_iprange', 'source_ipaddress', 'source_aggregate', 'source_service')
    )

    class Meta(NetBoxTable.Meta):
        model = ACLStandardRule
        fields = (
            "pk",
            "id",
            "access_list",
            "index",
            "action",
            "remark",
            "tags",
            "description",
            "source",
        )
        default_columns = (
            "access_list",
            "index",
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
    index = tables.Column(
        linkify=True,
    )
    action = ChoiceFieldColumn()
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:aclextendedrule_list",
    )
    source = tables.TemplateColumn(
        template_code=COL_SOURCE_AND_DESTINATION_ASSIGNMENT.replace('#replaceme#', 'source'),
        order_by=('source_prefix', 'source_iprange', 'source_ipaddress', 'source_aggregate', 'source_service')
    )
    destination = tables.TemplateColumn(
        template_code=COL_SOURCE_AND_DESTINATION_ASSIGNMENT.replace('#replaceme#', 'destination'),
        order_by=('destination_prefix', 'destination_iprange', 'destination_ipaddress', 'destination_aggregate', 'destination_service')
    )
    protocol = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = ACLExtendedRule
        fields = (
            "pk",
            "id",
            "access_list",
            "index",
            "action",
            "remark",
            "tags",
            "description",
            "source",
            "source_ports",
            "destination",
            "destination_ports",
            "protocol",
        )
        default_columns = (
            "access_list",
            "index",
            "action",
            "remark",
            "tags",
            "source",
            "source_ports",
            "destination",         
            "destination_ports",
            "protocol",
        )


