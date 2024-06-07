import strawberry_django
from .. import filtersets, models
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

__all__ = (
    'AccessListFilter',
    'ACLInterfaceAssignmentFilter',
    'ACLExtendedRuleFilter',
    'ACLStandardRuleFilter',
)

@strawberry_django.filter(models.AccessList, lookups=True)
@autotype_decorator(filtersets.AccessListFilterSet)
class AccessListFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(models.ACLStandardRule, lookups=True)
@autotype_decorator(filtersets.ACLStandardRuleFilterSet)
class ACLStandardRuleFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(models.ACLExtendedRule, lookups=True)
@autotype_decorator(filtersets.ACLExtendedRuleFilterSet)
class ACLExtendedRuleFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(models.ACLInterfaceAssignment, lookups=True)
@autotype_decorator(filtersets.ACLInterfaceAssignmentFilterSet)
class ACLInterfaceAssignmentFilter(BaseFilterMixin):
    pass