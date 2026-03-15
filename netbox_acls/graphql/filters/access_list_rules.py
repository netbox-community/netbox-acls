from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup

from core.graphql.filters import ContentTypeFilter
from netbox.graphql.filters import NetBoxModelFilter

try:
    from strawberry_django import StrFilterLookup
except ImportError:
    from strawberry_django import FilterLookup as StrFilterLookup

from ... import models

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup, IntegerRangeArrayLookup

    from ..enums import (
        ACLProtocolEnum,
        ACLRuleActionEnum,
    )
    from .access_lists import AccessListFilter


__all__ = (
    "ACLExtendedRuleFilter",
    "ACLStandardRuleFilter",
)


@dataclass
class ACLRuleFilterMixin(NetBoxModelFilter):
    """
    Base GraphQL filter mixin for ACL Rule models.
    """

    access_list: Annotated["AccessListFilter", strawberry.lazy("netbox_acls.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    access_list_id: ID | None = strawberry_django.filter_field()
    sequence: Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")] | None = (
        strawberry_django.filter_field()
    )
    description: StrFilterLookup[str] | None = strawberry_django.filter_field()
    action: BaseFilterLookup[Annotated["ACLRuleActionEnum", strawberry.lazy("netbox_acls.graphql.enums")]] | None = (
        strawberry_django.filter_field()
    )

    # Remark
    remark: StrFilterLookup[str] | None = strawberry_django.filter_field()

    # Source
    source_type: Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    source_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ACLStandardRule, lookups=True)
class ACLStandardRuleFilter(ACLRuleFilterMixin):
    """
    GraphQL filter definition for the ACLStandardRule model.
    """

    pass


@strawberry_django.filter(models.ACLExtendedRule, lookups=True)
class ACLExtendedRuleFilter(ACLRuleFilterMixin):
    """
    GraphQL filter definition for the ACLExtendedRule model.
    """

    # Source
    source_port_ranges: (
        Annotated["IntegerRangeArrayLookup", strawberry.lazy("netbox.graphql.filter_lookups")] | None
    ) = strawberry_django.filter_field()

    # Destination
    destination_type: Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    destination_id: ID | None = strawberry_django.filter_field()
    destination_port_ranges: (
        Annotated["IntegerRangeArrayLookup", strawberry.lazy("netbox.graphql.filter_lookups")] | None
    ) = strawberry_django.filter_field()

    # Protocol
    protocol: BaseFilterLookup[Annotated["ACLProtocolEnum", strawberry.lazy("netbox_acls.graphql.enums")]] | None = (
        strawberry_django.filter_field()
    )
