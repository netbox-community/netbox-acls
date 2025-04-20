from typing import List

import strawberry
import strawberry_django

from .types import (
    AccessListType,
    ACLExtendedRuleType,
    ACLInterfaceAssignmentType,
    ACLStandardRuleType,
)


@strawberry.type(name="Query")
class NetBoxACLSQuery:
    """
    Defines the queries available to this plugin via the graphql api.
    """

    access_list: AccessListType = strawberry_django.field()
    access_list_list: List[AccessListType] = strawberry_django.field()

    acl_extended_rule: ACLExtendedRuleType = strawberry_django.field()
    acl_extended_rule_list: List[ACLExtendedRuleType] = strawberry_django.field()

    acl_standard_rule: ACLStandardRuleType = strawberry_django.field()
    acl_standard_rule_list: List[ACLStandardRuleType] = strawberry_django.field()

    acl_interface_assignment: ACLInterfaceAssignmentType = strawberry_django.field()
    acl_interface_assignment_list: List[ACLInterfaceAssignmentType] = strawberry_django.field()
