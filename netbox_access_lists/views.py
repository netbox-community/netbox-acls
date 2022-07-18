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
            table = tables.ACLExtendedRuleTable(instance.extended_acl_rules.all())
        elif instance.type == 'standard':
            table = tables.ACLStandardRuleTable(instance.standard_acl_rules.all())
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
# ACLStandardRule views
#

class ACLStandardRuleView(generic.ObjectView):
    queryset = models.ACLStandardRule.objects.all()


class ACLStandardRuleListView(generic.ObjectListView):
    queryset = models.ACLStandardRule.objects.all()
    table = tables.ACLStandardRuleTable
    filterset = filtersets.ACLStandardRuleFilterSet
    filterset_form = forms.ACLStandardRuleFilterForm


class ACLStandardRuleEditView(generic.ObjectEditView):
    queryset = models.ACLStandardRule.objects.all()
    form = forms.ACLStandardRuleForm


class ACLStandardRuleDeleteView(generic.ObjectDeleteView):
    queryset = models.ACLStandardRule.objects.all()


#
# ACLExtendedRule views
#

class ACLExtendedRuleView(generic.ObjectView):
    queryset = models.ACLExtendedRule.objects.all()


class ACLExtendedRuleListView(generic.ObjectListView):
    queryset = models.ACLExtendedRule.objects.all()
    table = tables.ACLExtendedRuleTable
    filterset = filtersets.ACLExtendedRuleFilterSet
    filterset_form = forms.ACLExtendedRuleFilterForm


class ACLExtendedRuleEditView(generic.ObjectEditView):
    queryset = models.ACLExtendedRule.objects.all()
    form = forms.ACLExtendedRuleForm


class ACLExtendedRuleDeleteView(generic.ObjectDeleteView):
    queryset = models.ACLExtendedRule.objects.all()
