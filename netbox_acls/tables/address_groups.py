"""
Define the table views for the address group models.
"""

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, PrimaryModelTable, columns

from ..models import ACLAddressGroup, ACLAddressGroupMember

__all__ = (
    "ACLAddressGroupMemberTable",
    "ACLAddressGroupTable",
)


class ACLAddressGroupTable(PrimaryModelTable):
    """
    Address group identity, family and membership count.
    """

    id = tables.Column(
        linkify=True,
    )
    name = tables.Column(
        linkify=True,
    )
    family = columns.ChoiceFieldColumn()
    member_count = tables.Column(
        verbose_name=_("Member Count"),
    )
    tags = columns.TagColumn(
        url_name="plugins:netbox_acls:acladdressgroup_list",
    )

    class Meta(PrimaryModelTable.Meta):
        model = ACLAddressGroup
        fields = (
            "pk",
            "id",
            "name",
            "family",
            "member_count",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "name",
            "family",
            "member_count",
            "description",
        )


class ACLAddressGroupMemberTable(NetBoxTable):
    """
    Membership rows retain links to both group and IPAM object.
    """

    id = tables.Column(
        linkify=True,
    )
    address_group = tables.Column(
        linkify=True,
    )
    member_type = columns.ContentTypeColumn()
    member = tables.Column(
        verbose_name=_("Member"),
        orderable=False,
        linkify=True,
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
        url_name="plugins:netbox_acls:acladdressgroupmember_list",
    )

    class Meta(NetBoxTable.Meta):
        model = ACLAddressGroupMember
        fields = (
            "pk",
            "id",
            "address_group",
            "member_type",
            "member",
            "owner",
            "comments",
            "tags",
        )
        default_columns = (
            "id",
            "address_group",
            "member_type",
            "member",
        )
