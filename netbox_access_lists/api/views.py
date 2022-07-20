"""
Create views to handle the API logic.
A view set is a single class that can handle the view, add, change,
and delete operations which each require dedicated views under the UI.
"""

from django.db.models import Count

from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import AccessListSerializer, ACLExtendedRuleSerializer, ACLStandardRuleSerializer


class AccessListViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django AccessList model & associates it to a view.
    """
    queryset = models.AccessList.objects.prefetch_related(
        'device', 'tags'
    ).annotate(
        rule_count=Count('aclextendedrules') + Count('aclstandardrules')
    )
    serializer_class = AccessListSerializer
    filterset_class = filtersets.AccessListFilterSet


class ACLStandardRuleViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLStandardRule model & associates it to a view.
    """
    queryset = models.ACLStandardRule.objects.prefetch_related(
        'access_list', 'tags', 'source_prefix'
    )
    serializer_class = ACLStandardRuleSerializer
    filterset_class = filtersets.ACLStandardRuleFilterSet


class ACLExtendedRuleViewSet(NetBoxModelViewSet):
    """
    Defines the view set for the django ACLExtendedRule model & associates it to a view.
    """
    queryset = models.ACLExtendedRule.objects.prefetch_related(
        'access_list', 'tags', 'source_prefix', 'destination_prefix',
    )
    serializer_class = ACLExtendedRuleSerializer
    filterset_class = filtersets.ACLExtendedRuleFilterSet
