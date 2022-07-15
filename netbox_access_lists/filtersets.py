from netbox.filtersets import NetBoxModelFilterSet
from .models import AccessList, AccessListExtendedRule


class AccessListFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AccessList
        fields = ('id', 'name', 'device', 'type', 'default_action', 'comments')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)


class AccessListExtendedRuleFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = AccessListExtendedRule
        fields = ('id', 'access_list', 'index', 'protocol', 'action', 'remark')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)
