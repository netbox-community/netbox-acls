from graphene import ObjectType
from netbox.graphql.fields import ObjectField, ObjectListField

from .types import *


class Query(ObjectType):
    """
    Defines the queries available to this plugin via the graphql api.
    """

    access_list = ObjectField(AccessListType)
    access_list_list = ObjectListField(AccessListType)

    acl_extended_rule = ObjectField(ACLExtendedRuleType)
    acl_extended_rule_list = ObjectListField(ACLExtendedRuleType)

    acl_standard_rule = ObjectField(ACLStandardRuleType)
    acl_standard_rule_list = ObjectListField(ACLStandardRuleType)


schema = Query
