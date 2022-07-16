from django.db.models import Count

from netbox.views import generic
from . import filtersets, forms, models, tables


#
# AccessList views
#

class AccessListView(generic.ObjectView):
    queryset = models.AccessList.objects.all()

    def get_extra_context(self, request, instance):
        if instance.type == 'extended':
            table = tables.AccessListExtendedRuleTable(instance.extended_acl_rules.all())
        elif instance.type == 'standard':
            table = tables.AccessListStandardRuleTable(instance.standard_acl_rules.all())
        table.configure(request)

        return {
            'rules_table': table
        }


class AccessListListView(generic.ObjectListView):
    queryset = models.AccessList.objects.annotate(
        rule_count=Count('extended_acl_rules') + Count('standard_acl_rules')
    )
    table = tables.AccessListTable
    filterset = filtersets.AccessListFilterSet
    filterset_form = forms.AccessListFilterForm


class AccessListEditView(generic.ObjectEditView):
    queryset = models.AccessList.objects.all()
    form = forms.AccessListForm


class AccessListDeleteView(generic.ObjectDeleteView):
    queryset = models.AccessList.objects.all()


#
# AccessListStandardRule views
#

class AccessListStandardRuleView(generic.ObjectView):
    queryset = models.AccessListStandardRule.objects.all()


class AccessListStandardRuleListView(generic.ObjectListView):
    queryset = models.AccessListStandardRule.objects.all()
    table = tables.AccessListStandardRuleTable
    filterset = filtersets.AccessListStandardRuleFilterSet
    filterset_form = forms.AccessListStandardRuleFilterForm


class AccessListStandardRuleEditView(generic.ObjectEditView):
    queryset = models.AccessListStandardRule.objects.all()
    form = forms.AccessListStandardRuleForm


class AccessListStandardRuleDeleteView(generic.ObjectDeleteView):
    queryset = models.AccessListStandardRule.objects.all()


#
# AccessListExtendedRule views
#

class AccessListExtendedRuleView(generic.ObjectView):
    queryset = models.AccessListExtendedRule.objects.all()


class AccessListExtendedRuleListView(generic.ObjectListView):
    queryset = models.AccessListExtendedRule.objects.all()
    table = tables.AccessListExtendedRuleTable
    filterset = filtersets.AccessListExtendedRuleFilterSet
    filterset_form = forms.AccessListExtendedRuleFilterForm


class AccessListExtendedRuleEditView(generic.ObjectEditView):
    queryset = models.AccessListExtendedRule.objects.all()
    form = forms.AccessListExtendedRuleForm


class AccessListExtendedRuleDeleteView(generic.ObjectDeleteView):
    queryset = models.AccessListExtendedRule.objects.all()
