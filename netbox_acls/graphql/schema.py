import strawberry
import strawberry_django

from .types import (
    AccessListType,
    ACLAssignmentType,
    ACLExtendedRuleType,
    ACLStandardRuleType,
)


@strawberry.type(name="Query")
class NetBoxACLSQuery:
    """
    Defines the queries available to this plugin via the graphql api.
    """

    access_list: AccessListType = strawberry_django.field()
    access_list_list: list[AccessListType] = strawberry_django.field()

    acl_extended_rule: ACLExtendedRuleType = strawberry_django.field()
    acl_extended_rule_list: list[ACLExtendedRuleType] = strawberry_django.field()

    acl_standard_rule: ACLStandardRuleType = strawberry_django.field()
    acl_standard_rule_list: list[ACLStandardRuleType] = strawberry_django.field()

    acl_assignment: ACLAssignmentType = strawberry_django.field()
    acl_assignment_list: list[ACLAssignmentType] = strawberry_django.field()
