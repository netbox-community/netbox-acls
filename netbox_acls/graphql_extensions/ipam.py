"""ACL additions to NetBox's IPAM GraphQL types."""

import strawberry

from .base import ACLAddressGroupMemberReferences, ACLRuleReferences

__all__ = (
    "AggregateTypeExtension",
    "IPAddressTypeExtension",
    "IPRangeTypeExtension",
    "PrefixTypeExtension",
)


@strawberry.type
class AggregateTypeExtension(ACLAddressGroupMemberReferences, ACLRuleReferences):
    """ACL additions to NetBox's Aggregate type."""

    models = ["ipam.aggregate"]


@strawberry.type
class IPAddressTypeExtension(ACLAddressGroupMemberReferences, ACLRuleReferences):
    """ACL additions to NetBox's IPAddress type."""

    models = ["ipam.ipaddress"]


@strawberry.type
class IPRangeTypeExtension(ACLAddressGroupMemberReferences, ACLRuleReferences):
    """ACL additions to NetBox's IPRange type."""

    models = ["ipam.iprange"]


@strawberry.type
class PrefixTypeExtension(ACLAddressGroupMemberReferences, ACLRuleReferences):
    """ACL additions to NetBox's Prefix type."""

    models = ["ipam.prefix"]
