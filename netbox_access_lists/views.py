from django.db.models import Count

from netbox.views import generic
from . import filtersets, forms, models, tables


#
# AccessList views
#

class AccessListView(generic.ObjectView):
    queryset = models.AccessList.objects.all()

    def get_extra_context(self, request, instance):
        table = tables.AccessListExtendedRuleTable(instance.rules.all())
        table.configure(request)

        return {
            'rules_table': table,
        }


class AccessListListView(generic.ObjectListView):
    queryset = models.AccessList.objects.annotate(
        rule_count=Count('rules')
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
