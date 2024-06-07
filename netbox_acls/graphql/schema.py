import strawberry
import strawberry_django
from .types import *
from ..models import *

@strawberry.type
class NetBoxACLSAccessListQuery:
    """
    Defines the queries available to this plugin via the graphql api.
    """
    @strawberry.field
    def access_list(self, id: int) -> AccessListType:
        return AccessList.objects.get(pk=id)
    access_list_list: list[AccessListType] = strawberry_django.field()

@strawberry.type
class NetBoxACLSACLExtendedRuleQuery:
    @strawberry.field
    def acl_extended_rule(self, id: int) -> ACLExtendedRuleType:
        return ACLExtendedRule.objects.get(pk=id)
    acl_extended_rule_list: list[ACLExtendedRuleType] = strawberry_django.field()



@strawberry.type
class NetBoxACLSStandardRuleQuery:
    @strawberry.field
    def acl_standard_rule(self, id: int) -> ACLStandardRuleType:
        return ACLStandardRule.objects.get(pk=id)
    acl_standard_rule_list: list[ACLStandardRuleType] = strawberry_django.field()


