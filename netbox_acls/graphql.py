"""
Define the object types and queries availble via the graphql api.
"""

from graphene import ObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from . import filtersets, models

__all__ = (
    "AccessListType",
    "ACLInterfaceAssignmentType",
    "ACLExtendedRuleType",
    "ACLStandardRuleType",
)

#
# Object types
#


class AccessListType(NetBoxObjectType):
    """
    Defines the object type for the django model AccessList.
    """

    class Meta:
        """
        Associates the filterset, fields, and model for the django model AccessList.
        """

        model = models.AccessList
        fields = "__all__"
        filterset_class = filtersets.AccessListFilterSet


class ACLInterfaceAssignmentType(NetBoxObjectType):
    """
    Defines the object type for the django model AccessList.
    """

    class Meta:
        """
        Associates the filterset, fields, and model for the django model ACLInterfaceAssignment.
        """

        model = models.ACLInterfaceAssignment
        fields = "__all__"
        filterset_class = filtersets.ACLInterfaceAssignmentFilterSet


class ACLExtendedRuleType(NetBoxObjectType):
    """
    Defines the object type for the django model ACLExtendedRule.
    """

    class Meta:
        """
        Associates the filterset, fields, and model for the django model ACLExtendedRule.
        """

        model = models.ACLExtendedRule
        fields = "__all__"
        filterset_class = filtersets.ACLExtendedRuleFilterSet


class ACLStandardRuleType(NetBoxObjectType):
    """
    Defines the object type for the django model ACLStandardRule.
    """

    class Meta:
        """
        Associates the filterset, fields, and model for the django model ACLStandardRule.
        """

        model = models.ACLStandardRule
        fields = "__all__"
        filterset_class = filtersets.ACLStandardRuleFilterSet


#
# Queries
#


class Query(ObjectType):
    """
    Defines the queries availible to this plugin via the graphql api.
    """

    access_list = ObjectField(AccessListType)
    access_list_list = ObjectListField(AccessListType)

    acl_extended_rule = ObjectField(ACLExtendedRuleType)
    acl_extended_rule_list = ObjectListField(ACLExtendedRuleType)

    acl_standard_rule = ObjectField(ACLStandardRuleType)
    acl_standard_rule_list = ObjectListField(ACLStandardRuleType)


schema = Query
