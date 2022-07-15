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


class AccessListExtendedRuleType(NetBoxObjectType):

    class Meta:
        model = models.AccessListExtendedRule
        fields = '__all__'
        filterset_class = filtersets.AccessListExtendedRuleFilterSet


#class AccessListStandardRuleType(NetBoxObjectType):
#
#    class Meta:
#        model = models.AccessListStandardRule
#        fields = '__all__'
#        filterset_class = filtersets.AccessListStandardRuleFilterSet

#
# Queries
#

class Query(ObjectType):
    access_list = ObjectField(AccessListType)
    access_list_list = ObjectListField(AccessListType)

    access_list_rule = ObjectField(AccessListExtendedRuleType)
    access_list_rule_list = ObjectListField(AccessListExtendedRuleType)


#class Query(ObjectType):
#    access_list = ObjectField(AccessListType)
#    access_list_list = ObjectListField(AccessListType)
#
#    access_list_rule = ObjectField(AccessListStandardRuleType)
#    access_list_rule_list = ObjectListField(AccessListStandardRuleType)

schema = Query
