"""ACL additions to NetBox's IPAM GraphQL types."""

import strawberry

from .base import ACLRuleReferences

__all__ = (
    "AggregateTypeExtension",
    "IPAddressTypeExtension",
    "IPRangeTypeExtension",
    "PrefixTypeExtension",
)


@strawberry.type
class AggregateTypeExtension(ACLRuleReferences):
    """ACL additions to NetBox's Aggregate type."""

    models = ["ipam.aggregate"]


@strawberry.type
class IPAddressTypeExtension(ACLRuleReferences):
    """ACL additions to NetBox's IPAddress type."""

    models = ["ipam.ipaddress"]


@strawberry.type
class IPRangeTypeExtension(ACLRuleReferences):
    """ACL additions to NetBox's IPRange type."""

    models = ["ipam.iprange"]


@strawberry.type
class PrefixTypeExtension(ACLRuleReferences):
    """ACL additions to NetBox's Prefix type."""

    models = ["ipam.prefix"]
