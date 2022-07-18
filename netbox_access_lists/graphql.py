from graphene import ObjectType
from netbox.graphql.types import NetBoxObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from . import filtersets, models


#
# Object types
#

class AccessListType(NetBoxObjectType):

    class Meta:
        model = models.AccessList
        fields = '__all__'
        filterset_class = filtersets.AccessListFilterSet


class ACLExtendedRuleType(NetBoxObjectType):

    class Meta:
        model = models.ACLExtendedRule
        fields = '__all__'
        filterset_class = filtersets.ACLExtendedRuleFilterSet


class ACLStandardRuleType(NetBoxObjectType):

    class Meta:
        model = models.ACLStandardRule
        fields = '__all__'
        filterset_class = filtersets.ACLStandardRuleFilterSet

#
# Queries
#

class Query(ObjectType):
    access_list = ObjectField(AccessListType)
    access_list_list = ObjectListField(AccessListType)

    access_list_rule = ObjectField(ACLExtendedRuleType)
    access_list_rule_list = ObjectListField(ACLExtendedRuleType)


#class Query(ObjectType):
#    access_list = ObjectField(AccessListType)
#    access_list_list = ObjectListField(AccessListType)
#
#    access_list_rule = ObjectField(ACLStandardRuleType)
#    access_list_rule_list = ObjectListField(ACLStandardRuleType)

schema = Query
