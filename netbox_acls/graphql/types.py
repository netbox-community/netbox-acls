"""
Define the object types and queries availble via the graphql api.
"""

from netbox.graphql.types import NetBoxObjectType

from .. import filtersets, models

__all__ = (
    "AccessListType",
    "ACLInterfaceAssignmentType",
    "ACLExtendedRuleType",
    "ACLStandardRuleType",
)


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
