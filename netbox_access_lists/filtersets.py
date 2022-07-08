from netbox.filtersets import NetBoxModelFilterSet
from .models import AccessList, AccessListRule


class AccessListFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AccessList
        fields = ('id', 'name', 'type', 'default_action', 'comments')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)


class AccessListRuleFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = AccessListRule
        fields = ('id', 'access_list', 'index', 'protocol', 'action')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)
