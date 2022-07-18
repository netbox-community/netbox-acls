from django.db.models import Count

from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import AccessListSerializer, ACLExtendedRuleSerializer, ACLStandardRuleSerializer


class AccessListViewSet(NetBoxModelViewSet):
    queryset = models.AccessList.objects.prefetch_related(
        'device', 'tags'
    ).annotate(
        rule_count=Count('aclextendedrules') + Count('aclstandardrules')
    )
    serializer_class = AccessListSerializer
    filterset_class = filtersets.AccessListFilterSet


class ACLStandardRuleViewSet(NetBoxModelViewSet):
    queryset = models.ACLStandardRule.objects.prefetch_related(
        'access_list', 'tags', 'source_prefix'
    )
    serializer_class = ACLStandardRuleSerializer
    filterset_class = filtersets.ACLStandardRuleFilterSet


class ACLExtendedRuleViewSet(NetBoxModelViewSet):
    queryset = models.ACLExtendedRule.objects.prefetch_related(
        'access_list', 'tags', 'source_prefix', 'destination_prefix',
    )
    serializer_class = ACLExtendedRuleSerializer
    filterset_class = filtersets.ACLExtendedRuleFilterSet
