from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from ... import models

if TYPE_CHECKING:
    from ipam.graphql.filters import PrefixFilter
    from netbox.graphql.filter_lookups import IntegerArrayLookup, IntegerLookup

    from ..enums import (
        ACLProtocolEnum,
        ACLRuleActionEnum,
    )
    from .access_lists import AccessListFilter


__all__ = (
    "ACLStandardRuleFilter",
    "ACLExtendedRuleFilter",
)


@dataclass
class ACLRuleFilterMixin(NetBoxModelFilterMixin):
    """
    Base GraphQL filter mixin for ACL Rule models.
    """

    access_list: Annotated["AccessListFilter", strawberry.lazy("netbox_acls.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    access_list_id: ID | None = strawberry_django.filter_field()
    index: Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")] | None = (
        strawberry_django.filter_field()
    )
    remark: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    action: Annotated["ACLRuleActionEnum", strawberry.lazy("netbox_acls.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    source_prefix: Annotated["PrefixFilter", strawberry.lazy("ipam.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )


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

    source_ports: Annotated["IntegerArrayLookup", strawberry.lazy("netbox.graphql.filter_lookups")] | None = (
        strawberry_django.filter_field()
    )
    destination_prefix: Annotated["PrefixFilter", strawberry.lazy("ipam.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    destination_ports: Annotated["IntegerArrayLookup", strawberry.lazy("netbox.graphql.filter_lookups")] | None = (
        strawberry_django.filter_field()
    )
    protocol: Annotated["ACLProtocolEnum", strawberry.lazy("netbox_acls.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
