from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, StrFilterLookup

from core.graphql.filters import ContentTypeFilter
from netbox.graphql.filters import NetBoxModelFilter, PrimaryModelFilter

from ... import models

if TYPE_CHECKING:
    from ..enums import ACLAddressFamilyEnum


__all__ = (
    "ACLAddressGroupFilter",
    "ACLAddressGroupMemberFilter",
)


@strawberry_django.filter_type(models.ACLAddressGroup, lookups=True)
class ACLAddressGroupFilter(PrimaryModelFilter):
    """
    GraphQL filter definition for the ACLAddressGroup model.
    """

    name: StrFilterLookup | None = strawberry_django.filter_field()
    family: BaseFilterLookup[Annotated["ACLAddressFamilyEnum", strawberry.lazy("netbox_acls.graphql.enums")]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ACLAddressGroupMember, lookups=True)
class ACLAddressGroupMemberFilter(NetBoxModelFilter):
    """
    GraphQL filter definition for the ACLAddressGroupMember model.
    """

    address_group: Annotated["ACLAddressGroupFilter", strawberry.lazy("netbox_acls.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    address_group_id: ID | None = strawberry_django.filter_field()
    member_type: Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    member_id: ID | None = strawberry_django.filter_field()
    comments: StrFilterLookup | None = strawberry_django.filter_field()
