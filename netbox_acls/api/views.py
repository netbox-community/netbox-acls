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
    ACLAssignmentSerializer,
    ACLExtendedRuleSerializer,
    ACLStandardRuleSerializer,
)

__all__ = [
    "ACLAssignmentViewSet",
    "ACLExtendedRuleViewSet",
    "ACLStandardRuleViewSet",
    "AccessListViewSet",
]


class AccessListViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django AccessList model and associates it with a view.
    """

    queryset = (
        models.AccessList.objects.annotate(rule_count=Count("aclextendedrules") + Count("aclstandardrules"))
        .select_related("owner")
        .prefetch_related("tags")
    )
    serializer_class = AccessListSerializer
    filterset_class = filtersets.AccessListFilterSet


class ACLAssignmentViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLInterfaceAssignment model and associates it with a view.
    """

    queryset = models.ACLAssignment.objects.select_related("owner").prefetch_related(
        "access_list",
        "assigned_object",
        "tags",
    )
    serializer_class = ACLAssignmentSerializer
    filterset_class = filtersets.ACLAssignmentFilterSet


class ACLStandardRuleViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLStandardRule model and associates it with a view.
    """

    queryset = models.ACLStandardRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "tags",
    )
    serializer_class = ACLStandardRuleSerializer
    filterset_class = filtersets.ACLStandardRuleFilterSet


class ACLExtendedRuleViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLExtendedRule model and associates it with a view.
    """

    queryset = models.ACLExtendedRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )
    serializer_class = ACLExtendedRuleSerializer
    filterset_class = filtersets.ACLExtendedRuleFilterSet
