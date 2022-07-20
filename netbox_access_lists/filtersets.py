"""
Filters enable users to request only a specific subset of objects matching a query;
when filtering the sites list by status or region, for instance.
"""

from netbox.filtersets import NetBoxModelFilterSet

from .models import *

__all__ = (
    'AccessListFilterSet',
    'ACLStandardRuleFilterSet',
    'ACLExtendedRuleFilterSet',
)


class AccessListFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model AccessList.
    """

    class Meta:
        """
        Associates the django model AccessList & fields to the filter set.
        """
        model = AccessList
        fields = ('id', 'name', 'device', 'type', 'default_action', 'comments')

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        return queryset.filter(description__icontains=value)


class ACLStandardRuleFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLStandardRule.
    """

    class Meta:
        """
        Associates the django model ACLStandardRule & fields to the filter set.
        """
        model = ACLStandardRule
        fields = ('id', 'access_list', 'index', 'action')

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        return queryset.filter(description__icontains=value)


class ACLExtendedRuleFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLExtendedRule.
    """

    class Meta:
        """
        Associates the django model ACLExtendedRule & fields to the filter set.
        """
        model = ACLExtendedRule
        fields = ('id', 'access_list', 'index', 'action', 'protocol')

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        return queryset.filter(description__icontains=value)
