"""
Serializers control the translation of client data to and from Python objects,
while Django itself handles the database abstraction.
"""

from netbox.api.serializers import WritableNestedSerializer
from rest_framework import serializers

from ..models import (
    AccessList,
    ACLExtendedRule,
    ACLInterfaceAssignment,
    ACLStandardRule,
)

__all__ = [
    "NestedAccessListSerializer",
    "NestedACLInterfaceAssignmentSerializer",
    "NestedACLStandardRuleSerializer",
    "NestedACLExtendedRuleSerializer",
]


class NestedAccessListSerializer(WritableNestedSerializer):
    """
    Defines the nested serializer for the django AccessList model & associates it to a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:accesslist-detail",
    )

    class Meta:
        """
        Associates the django model ACLStandardRule & fields to the nested serializer.
        """

        model = AccessList
        fields = ("id", "url", "display", "name")


class NestedACLInterfaceAssignmentSerializer(WritableNestedSerializer):
    """
    Defines the nested serializer for the django ACLInterfaceAssignment model & associates it to a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclinterfaceassignment-detail",
    )

    class Meta:
        """
        Associates the django model ACLInterfaceAssignment & fields to the nested serializer.
        """

        model = ACLInterfaceAssignment
        fields = ("id", "url", "display", "access_list")


class NestedACLStandardRuleSerializer(WritableNestedSerializer):
    """
    Defines the nested serializer for the django ACLStandardRule model & associates it to a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclstandardrule-detail",
    )

    class Meta:
        """
        Associates the django model ACLStandardRule & fields to the nested serializer.
        """

        model = ACLStandardRule
        fields = ("id", "url", "display", "index")


class NestedACLExtendedRuleSerializer(WritableNestedSerializer):
    """
    Defines the nested serializer for the django ACLExtendedRule model & associates it to a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclextendedrule-detail",
    )

    class Meta:
        """
        Associates the django model ACLExtendedRule & fields to the nested serializer.
        """

        model = ACLExtendedRule
        fields = ("id", "url", "display", "index")
