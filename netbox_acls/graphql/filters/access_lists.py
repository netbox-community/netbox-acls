from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, StrFilterLookup

from core.graphql.filters import ContentTypeFilter
from netbox.graphql.filters import NetBoxModelFilter, PrimaryModelFilter

from ... import models

if TYPE_CHECKING:
    from ..enums import (
        ACLActionEnum,
        ACLAssignmentDirectionEnum,
        ACLFamilyEnum,
        ACLTypeEnum,
    )


__all__ = (
    "ACLAssignmentFilter",
    "AccessListFilter",
)


@strawberry_django.filter_type(models.AccessList, lookups=True)
class AccessListFilter(PrimaryModelFilter):
    """
    GraphQL filter definition for the AccessList model.
    """

    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    type: BaseFilterLookup[Annotated["ACLTypeEnum", strawberry.lazy("netbox_acls.graphql.enums")]] | None = (
        strawberry_django.filter_field()
    )
    family: BaseFilterLookup[Annotated["ACLFamilyEnum", strawberry.lazy("netbox_acls.graphql.enums")]] | None = (
        strawberry_django.filter_field()
    )
    default_action: (
        BaseFilterLookup[Annotated["ACLActionEnum", strawberry.lazy("netbox_acls.graphql.enums")]] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACLAssignment, lookups=True)
class ACLAssignmentFilter(NetBoxModelFilter):
    """
    GraphQL filter definition for the ACLAssignment model.
    """

    access_list: Annotated["AccessListFilter", strawberry.lazy("netbox_acls.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    access_list_id: ID | None = strawberry_django.filter_field()
    assigned_object_type: Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()
    direction: (
        BaseFilterLookup[Annotated["ACLAssignmentDirectionEnum", strawberry.lazy("netbox_acls.graphql.enums")]] | None
    ) = strawberry_django.filter_field()
    family: BaseFilterLookup[Annotated["ACLFamilyEnum", strawberry.lazy("netbox_acls.graphql.enums")]] | None = (
        strawberry_django.filter_field()
    )
    comments: StrFilterLookup[str] | None = strawberry_django.filter_field()
