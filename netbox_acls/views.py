"""
Defines the business logic for the plugin.
Specifically, all the various interactions with a client.
"""

from django.db.models import Count
from netbox.views import generic

from . import choices, filtersets, forms, models, tables

__all__ = (
    "AccessListView",
    "AccessListListView",
    "AccessListEditView",
    "AccessListDeleteView",
    "AccessListBulkDeleteView",
    "ACLInterfaceAssignmentView",
    "ACLInterfaceAssignmentListView",
    "ACLInterfaceAssignmentEditView",
    "ACLInterfaceAssignmentDeleteView",
    "ACLInterfaceAssignmentBulkDeleteView",
    "ACLStandardRuleView",
    "ACLStandardRuleListView",
    "ACLStandardRuleEditView",
    "ACLStandardRuleDeleteView",
    "ACLStandardRuleBulkDeleteView",
    "ACLExtendedRuleView",
    "ACLExtendedRuleListView",
    "ACLExtendedRuleEditView",
    "ACLExtendedRuleDeleteView",
    "ACLExtendedRuleBulkDeleteView",
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

        if instance.type == choices.ACLTypeChoices.TYPE_EXTENDED:
            table = tables.ACLExtendedRuleTable(instance.aclextendedrules.all())
        elif instance.type == choices.ACLTypeChoices.TYPE_STANDARD:
            table = tables.ACLStandardRuleTable(instance.aclstandardrules.all())
        else:
            table = None

        if table:
            table.columns.hide("access_list")
            table.configure(request)

            return {
                "rules_table": table,
            }
        return {}


class AccessListListView(generic.ObjectListView):
    """
    Defines the list view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.annotate(
        rule_count=Count("aclextendedrules") + Count("aclstandardrules"),
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
    template_name = "netbox_acls/accesslist_edit.html"


class AccessListDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.all()


class AccessListBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AccessList.objects.all()
    filterset = filtersets.AccessListFilterSet
    table = tables.AccessListTable


#
# ACLInterfaceAssignment views
#


class ACLInterfaceAssignmentView(generic.ObjectView):
    """
    Defines the view for the ACLInterfaceAssignments django model.
    """

    queryset = models.ACLInterfaceAssignment.objects.all()


class ACLInterfaceAssignmentListView(generic.ObjectListView):
    """
    Defines the list view for the ACLInterfaceAssignments django model.
    """

    queryset = models.ACLInterfaceAssignment.objects.all()
    table = tables.ACLInterfaceAssignmentTable
    filterset = filtersets.ACLInterfaceAssignmentFilterSet
    filterset_form = forms.ACLInterfaceAssignmentFilterForm


class ACLInterfaceAssignmentEditView(generic.ObjectEditView):
    """
    Defines the edit view for the ACLInterfaceAssignments django model.
    """

    queryset = models.ACLInterfaceAssignment.objects.all()
    form = forms.ACLInterfaceAssignmentForm
    template_name = "netbox_acls/aclinterfaceassignment_edit.html"

    def get_extra_addanother_params(self, request):
        """
        Returns a dictionary of additional parameters to be passed to the "Add Another" button.
        """

        return {
            "access_list": request.GET.get("access_list")
            or request.POST.get("access_list"),
            "direction": request.GET.get("direction") or request.POST.get("direction"),
        }


class ACLInterfaceAssignmentDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLInterfaceAssignments django model.
    """

    queryset = models.ACLInterfaceAssignment.objects.all()


class ACLInterfaceAssignmentBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ACLInterfaceAssignment.objects.all()
    filterset = filtersets.ACLInterfaceAssignmentFilterSet
    table = tables.ACLInterfaceAssignmentTable


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

    def get_extra_addanother_params(self, request):
        """
        Returns a dictionary of additional parameters to be passed to the "Add Another" button.
        """

        return {
            "access_list": request.GET.get("access_list")
            or request.POST.get("access_list"),
        }


class ACLStandardRuleDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLStandardRules django model.
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

    def get_extra_addanother_params(self, request):
        """
        Returns a dictionary of additional parameters to be passed to the "Add Another" button.
        """

        return {
            "access_list": request.GET.get("access_list")
            or request.POST.get("access_list"),
        }


class ACLExtendedRuleDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLExtendedRules django model.
    """

    queryset = models.ACLExtendedRule.objects.all()


class ACLExtendedRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ACLExtendedRule.objects.all()
    filterset = filtersets.ACLExtendedRuleFilterSet
    table = tables.ACLExtendedRuleTable
