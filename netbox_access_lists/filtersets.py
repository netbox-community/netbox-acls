from netbox.filtersets import NetBoxModelFilterSet
from .models import AccessList, ACLExtendedRule, ACLStandardRule


class AccessListFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AccessList
        fields = ('id', 'name', 'device', 'type', 'default_action', 'comments')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)


class ACLStandardRuleFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = ACLStandardRule
        fields = ('id', 'access_list', 'index', 'action')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)


class ACLExtendedRuleFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = ACLExtendedRule
        fields = ('id', 'access_list', 'index', 'action', 'protocol')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)
