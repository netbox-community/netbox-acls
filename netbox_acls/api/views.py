"""
Create views to handle the API logic.
A view set is a single class that can handle the view, add, change,
and delete operations which each require dedicated views under the UI.
"""

from django.db.models import Count

from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import (
    AccessListSerializer,
    ACLAddressGroupMemberSerializer,
    ACLAddressGroupSerializer,
    ACLAssignmentSerializer,
    ACLExtendedRuleSerializer,
    ACLStandardRuleSerializer,
)

__all__ = [
    "ACLAddressGroupMemberViewSet",
    "ACLAddressGroupViewSet",
    "ACLAssignmentViewSet",
    "ACLExtendedRuleViewSet",
    "ACLStandardRuleViewSet",
    "AccessListViewSet",
]


class AccessListViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django AccessList model and associates it with a view.
    """

    queryset = models.AccessList.objects.annotate(
        rule_count=Count("aclextendedrules") + Count("aclstandardrules")
    ).select_related("owner")
    serializer_class = AccessListSerializer
    filterset_class = filtersets.AccessListFilterSet


class ACLAssignmentViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLInterfaceAssignment model and associates it with a view.
    """

    queryset = models.ACLAssignment.objects.select_related("owner").prefetch_related(
        # Both referenced by ACLAssignment.__str__(), which backs display.
        "access_list",
        "assigned_object",
    )
    serializer_class = ACLAssignmentSerializer
    filterset_class = filtersets.ACLAssignmentFilterSet


class ACLStandardRuleViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLStandardRule model and associates it with a view.
    """

    # access_list is referenced by ACLRule.__str__(), which backs display.
    queryset = models.ACLStandardRule.objects.select_related("owner").prefetch_related("access_list")
    serializer_class = ACLStandardRuleSerializer
    filterset_class = filtersets.ACLStandardRuleFilterSet


class ACLExtendedRuleViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLExtendedRule model and associates it with a view.
    """

    # access_list is referenced by ACLRule.__str__(), which backs display.
    queryset = models.ACLExtendedRule.objects.select_related("owner").prefetch_related("access_list")
    serializer_class = ACLExtendedRuleSerializer
    filterset_class = filtersets.ACLExtendedRuleFilterSet


class ACLAddressGroupViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLAddressGroup model and associates it with a view.
    """

    queryset = models.ACLAddressGroup.objects.annotate(
        member_count=Count("acladdressgroupmembers", distinct=True)
    ).select_related("owner")
    serializer_class = ACLAddressGroupSerializer
    filterset_class = filtersets.ACLAddressGroupFilterSet


class ACLAddressGroupMemberViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLAddressGroupMember model and associates it with a view.
    """

    queryset = models.ACLAddressGroupMember.objects.select_related("owner").prefetch_related(
        # Both referenced by ACLAddressGroupMember.__str__(), which backs display.
        "address_group",
        "member",
    )
    serializer_class = ACLAddressGroupMemberSerializer
    filterset_class = filtersets.ACLAddressGroupMemberFilterSet
