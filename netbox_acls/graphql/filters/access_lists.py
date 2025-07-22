from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from core.graphql.filters import ContentTypeFilter
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from ... import models

if TYPE_CHECKING:
    from ..enums import (
        ACLActionEnum,
        ACLAssignmentDirectionEnum,
        ACLTypeEnum,
    )


__all__ = (
    "AccessListFilter",
    "ACLInterfaceAssignmentFilter",
)


@strawberry_django.filter(models.AccessList, lookups=True)
class AccessListFilter(NetBoxModelFilterMixin):
    """
    GraphQL filter definition for the AccessList model.
    """

    name: FilterLookup[str] | None = strawberry_django.filter_field()
    assigned_object_type: Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()
    type: Annotated["ACLTypeEnum", strawberry.lazy("netbox_acls.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    default_action: Annotated["ACLActionEnum", strawberry.lazy("netbox_acls.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ACLInterfaceAssignment, lookups=True)
class ACLInterfaceAssignmentFilter(NetBoxModelFilterMixin):
    """
    GraphQL filter definition for the ACLInterfaceAssignment model.
    """

    access_list: Annotated["AccessListFilter", strawberry.lazy("netbox_acls.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    access_list_id: ID | None = strawberry_django.filter_field()
    direction: Annotated["ACLAssignmentDirectionEnum", strawberry.lazy("netbox_acls.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_type: Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()
