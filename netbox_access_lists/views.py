"""
Defines the business logic for the plugin.
Specifically, all the various interactions with a client.
"""

from django.db.models import Count
from netbox.views import generic

from . import filtersets, forms, models, tables

__all__ = (
    'AccessListView',
    'AccessListListView',
    'AccessListEditView',
    'AccessListDeleteView',
    'AccessListBulkDeleteView',
    'ACLStandardRuleView',
    'ACLStandardRuleListView',
    'ACLStandardRuleEditView',
    'ACLStandardRuleDeleteView',
    'ACLStandardRuleBulkDeleteView',
    'ACLExtendedRuleView',
    'ACLExtendedRuleListView',
    'ACLExtendedRuleEditView',
    'ACLExtendedRuleDeleteView',
    'ACLExtendedRuleBulkDeleteView',
)


#
# AccessList views
#

class AccessListView(generic.ObjectView):
    """
    Defines the view for the AccessLists django model.
    """
    queryset = models.AccessList.objects.all()

    def get_extra_context(self, request, instance):
        """
        Depending on the Access List type, the list view will return the required ACL Rule using the previous defined tables in tables.py.
        """
        if instance.type == 'extended':
            table = tables.ACLExtendedRuleTable(instance.aclextendedrules.all())
        elif instance.type == 'standard':
            table = tables.ACLStandardRuleTable(instance.aclstandardrules.all())
        table.configure(request)

        return {
            'rules_table': table
        }


class AccessListListView(generic.ObjectListView):
    """
    Defines the list view for the AccessLists django model.
    """
    queryset = models.AccessList.objects.annotate(
        rule_count=Count('aclextendedrules') + Count('aclstandardrules')
    )
    table = tables.AccessListTable
    filterset = filtersets.AccessListFilterSet
    filterset_form = forms.AccessListFilterForm


class AccessListEditView(generic.ObjectEditView):
    """
    Defines the edit view for the AccessLists django model.
    """
    queryset = models.AccessList.objects.all()
    form = forms.AccessListForm
    template_name = 'netbox_access_lists/accesslist_edit.html'


class AccessListDeleteView(generic.ObjectDeleteView):
    """
    Defines the delete view for the AccessLists django model.
    """
    queryset = models.AccessList.objects.all()


class AccessListBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AccessList.objects.all()
    filterset = filtersets.AccessListFilterSet
    table = tables.AccessListTable


#class AccessListBulkEditView(generic.BulkEditView):
#    """
#    Defines the bulk edit view for the AccessList django model.
#    """
#    queryset = models.AccessList.objects.annotate(
#        rule_count=Count('aclextendedrules') + Count('aclstandardrules')
#    )
#    table = tables.AccessListTable
#    filterset = filtersets.AccessListFilterSet
#    form = forms.AccessListBulkEditForm

#
# ACLStandardRule views
#


class ACLStandardRuleView(generic.ObjectView):
    """
    Defines the view for the ACLStandardRule django model.
    """
    queryset = models.ACLStandardRule.objects.all()


class ACLStandardRuleListView(generic.ObjectListView):
    """
    Defines the list view for the ACLStandardRule django model.
    """
    queryset = models.ACLStandardRule.objects.all()
    table = tables.ACLStandardRuleTable
    filterset = filtersets.ACLStandardRuleFilterSet
    filterset_form = forms.ACLStandardRuleFilterForm


class ACLStandardRuleEditView(generic.ObjectEditView):
    """
    Defines the edit view for the ACLStandardRule django model.
    """
    queryset = models.ACLStandardRule.objects.all()
    form = forms.ACLStandardRuleForm


class ACLStandardRuleDeleteView(generic.ObjectDeleteView):
    """
    Defines the delete view for the ACLStandardRules django model.
    """
    queryset = models.ACLStandardRule.objects.all()


class ACLStandardRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ACLStandardRule.objects.all()
    filterset = filtersets.ACLStandardRuleFilterSet
    table = tables.ACLStandardRuleTable

#
# ACLExtendedRule views
#


class ACLExtendedRuleView(generic.ObjectView):
    """
    Defines the view for the ACLExtendedRule django model.
    """
    queryset = models.ACLExtendedRule.objects.all()


class ACLExtendedRuleListView(generic.ObjectListView):
    """
    Defines the list view for the ACLExtendedRule django model.
    """
    queryset = models.ACLExtendedRule.objects.all()
    table = tables.ACLExtendedRuleTable
    filterset = filtersets.ACLExtendedRuleFilterSet
    filterset_form = forms.ACLExtendedRuleFilterForm


class ACLExtendedRuleEditView(generic.ObjectEditView):
    """
    Defines the edit view for the ACLExtendedRule django model.
    """
    queryset = models.ACLExtendedRule.objects.all()
    form = forms.ACLExtendedRuleForm


class ACLExtendedRuleDeleteView(generic.ObjectDeleteView):
    """
    Defines the delete view for the ACLExtendedRules django model.
    """
    queryset = models.ACLExtendedRule.objects.all()

class ACLExtendedRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ACLExtendedRule.objects.all()
    filterset = filtersets.ACLExtendedRuleFilterSet
    table = tables.ACLExtendedRuleTable
