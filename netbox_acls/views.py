"""
Defines the business logic for the plugin.
Specifically, all the various interactions with a client.
"""

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from dcim.models import Device, Interface, VirtualChassis
from django.db.models import Count
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from virtualization.models import VirtualMachine, VMInterface

from . import choices, filtersets, forms, models, tables

__all__ = (
    "AccessListView",
    "AccessListListView",
    "AccessListEditView",
    "AccessListDeleteView",
    "AccessListBulkDeleteView",
    "ACLAssignmentView",
    "ACLAssignmentListView",
    "ACLAssignmentEditView",
    "ACLAssignmentDeleteView",
    "ACLAssignmentBulkDeleteView",
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
# Base children views
#


class ACLAssignmentChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACL Assignments."""

    child_model = models.ACLAssignment
    filterset = filtersets.ACLAssignmentFilterSet
    tab = ViewTab(
        label=_("Access Lists"),
        badge=lambda obj: obj.aclassignments.count(),
        permission="netbox_acls.view_aclassignment",
        weight=1100,
    )
    table = tables.ACLAssignmentTable

    def get_children(self, request, parent):
        """
        Return all objects of ACLAssignment.
        """
        return models.ACLAssignment.objects.restrict(request.user, "view").prefetch_related(
            "access_list",
            "assigned_object_type",
            "assigned_object",
            "tags",
        )

    def get_extra_context(self, request, instance) -> dict:
        """
        Return ContentType as extra context.
        """
        assigned_object_type = ContentType.objects.get_for_model(self.queryset.model)

        return super().get_extra_context(request, instance) | {
            "add_url": "plugins:netbox_acls:aclassignment_add",
            "content_type_id": assigned_object_type.id,
        }


#
# AccessList views
#


@register_model_view(models.AccessList)
class AccessListView(generic.ObjectView):
    """
    Defines the view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.prefetch_related("tags")

    def get_extra_context(self, request, instance):
        """
        Depending on the Access List type, the list view will return
        the required ACL Rule using the previously defined tables in tables.py.
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


@register_model_view(models.AccessList, "list", path="", detail=False)
class AccessListListView(generic.ObjectListView):
    """
    Defines the list view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.annotate(
        rule_count=Count("aclextendedrules") + Count("aclstandardrules"),
    ).prefetch_related("tags")
    table = tables.AccessListTable
    filterset = filtersets.AccessListFilterSet
    filterset_form = forms.AccessListFilterForm


@register_model_view(models.AccessList, "add", detail=False)
@register_model_view(models.AccessList, "edit")
class AccessListEditView(generic.ObjectEditView):
    """
    Defines the edit view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.prefetch_related("tags")
    form = forms.AccessListForm


@register_model_view(models.AccessList, "delete")
class AccessListDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.prefetch_related("tags")


@register_model_view(models.AccessList, "bulk_delete", path="delete", detail=False)
class AccessListBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AccessList.objects.prefetch_related("tags")
    filterset = filtersets.AccessListFilterSet
    table = tables.AccessListTable


#
# ACLAssignment views
#


@register_model_view(models.ACLAssignment)
class ACLAssignmentView(generic.ObjectView):
    """
    Defines the view for the ACLAssignments django model.
    """

    queryset = models.ACLAssignment.objects.prefetch_related(
        "access_list",
        "tags",
    )


@register_model_view(models.ACLAssignment, "list", path="", detail=False)
class ACLAssignmentListView(generic.ObjectListView):
    """
    Defines the list view for the ACLAssignments django model.
    """

    queryset = models.ACLAssignment.objects.prefetch_related(
        "access_list",
        "tags",
    )
    table = tables.ACLAssignmentTable
    filterset = filtersets.ACLAssignmentFilterSet
    filterset_form = forms.ACLAssignmentFilterForm


@register_model_view(models.ACLAssignment, "add", detail=False)
@register_model_view(models.ACLAssignment, "edit")
class ACLAssignmentEditView(generic.ObjectEditView):
    """
    Defines the edit view for the ACLAssignments django model.
    """

    queryset = models.ACLAssignment.objects.prefetch_related(
        "access_list",
        "tags",
    )
    form = forms.ACLAssignmentForm

    def get_extra_addanother_params(self, request):
        """
        Returns a dictionary of additional parameters to be passed to the "Add Another" button.
        """

        return {
            "access_list": request.GET.get("access_list") or request.POST.get("access_list"),
            "direction": request.GET.get("direction") or request.POST.get("direction"),
        }


@register_model_view(models.ACLAssignment, "delete")
class ACLAssignmentDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLAssignments django model.
    """

    queryset = models.ACLAssignment.objects.prefetch_related(
        "access_list",
        "tags",
    )


@register_model_view(models.ACLAssignment, "bulk_delete", path="delete", detail=False)
class ACLAssignmentBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ACLAssignment.objects.prefetch_related(
        "access_list",
        "tags",
    )
    filterset = filtersets.ACLAssignmentFilterSet
    table = tables.ACLAssignmentTable


@register_model_view(Device, "aclassignments", path="access-lists")
class DeviceACLAssignmentView(ACLAssignmentChildrenView):
    """
    Children view of ACL Assignment of Devices.
    """

    queryset = Device.objects.all()
    template_name = "inc/view_tab.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(device=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with the assigned object colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide the assigned object type column
        table.columns.hide("assigned_object_type")
        # Hide the assigned object column
        table.columns.hide("assigned_object")
        # Hide the direction column
        table.columns.hide("direction")

        return table


@register_model_view(Interface, "aclassignments", path="access-lists")
class InterfaceACLAssignmentView(ACLAssignmentChildrenView):
    """
    Children view of ACL Assignment of Interfaces.
    """

    queryset = Interface.objects.all()
    template_name = "inc/view_tab.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(interface=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with the assigned object colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide the assigned object type column
        table.columns.hide("assigned_object_type")
        # Hide the assigned object column
        table.columns.hide("assigned_object")

        return table


@register_model_view(VirtualChassis, "aclassignments", path="access-lists")
class VirtualChassisACLAssignmentView(ACLAssignmentChildrenView):
    """
    Children view of ACL Assignment of VirtualChassiss.
    """

    queryset = VirtualChassis.objects.all()
    template_name = "inc/view_tab.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(virtual_chassis=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with the assigned object colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide the assigned object type column
        table.columns.hide("assigned_object_type")
        # Hide the assigned object column
        table.columns.hide("assigned_object")
        # Hide the direction column
        table.columns.hide("direction")

        return table


@register_model_view(VirtualMachine, "aclassignments", path="access-lists")
class VirtualMachineACLAssignmentView(ACLAssignmentChildrenView):
    """
    Children view of ACL Assignment of VirtualMachines.
    """

    queryset = VirtualMachine.objects.all()
    template_name = "inc/view_tab.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(virtual_machine=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with the assigned object colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide the assigned object type column
        table.columns.hide("assigned_object_type")
        # Hide the assigned object column
        table.columns.hide("assigned_object")
        # Hide the direction column
        table.columns.hide("direction")

        return table


@register_model_view(VMInterface, "aclassignments", path="access-lists")
class VMInterfaceACLAssignmentView(ACLAssignmentChildrenView):
    """
    Children view of ACL Assignment of VMInterfaces.
    """

    queryset = VMInterface.objects.all()
    template_name = "inc/view_tab.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(vminterface=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with the assigned object colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide the assigned object type column
        table.columns.hide("assigned_object_type")
        # Hide the assigned object column
        table.columns.hide("assigned_object")

        return table


#
# ACLStandardRule views
#


@register_model_view(models.ACLStandardRule)
class ACLStandardRuleView(generic.ObjectView):
    """
    Defines the view for the ACLStandardRule django model.
    """

    queryset = models.ACLStandardRule.objects.prefetch_related(
        "access_list",
        "source",
        "tags",
    )


@register_model_view(models.ACLStandardRule, "list", path="", detail=False)
class ACLStandardRuleListView(generic.ObjectListView):
    """
    Defines the list view for the ACLStandardRule django model.
    """

    queryset = models.ACLStandardRule.objects.prefetch_related(
        "access_list",
        "source",
        "tags",
    )
    table = tables.ACLStandardRuleTable
    filterset = filtersets.ACLStandardRuleFilterSet
    filterset_form = forms.ACLStandardRuleFilterForm


@register_model_view(models.ACLStandardRule, "add", detail=False)
@register_model_view(models.ACLStandardRule, "edit")
class ACLStandardRuleEditView(generic.ObjectEditView):
    """
    Defines the edit view for the ACLStandardRule django model.
    """

    queryset = models.ACLStandardRule.objects.prefetch_related(
        "access_list",
        "source",
        "tags",
    )
    form = forms.ACLStandardRuleForm

    def get_extra_addanother_params(self, request):
        """
        Returns a dictionary of additional parameters to be passed to the "Add Another" button.
        """

        return {
            "access_list": request.GET.get("access_list") or request.POST.get("access_list"),
        }


@register_model_view(models.ACLStandardRule, "delete")
class ACLStandardRuleDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLStandardRules django model.
    """

    queryset = models.ACLStandardRule.objects.prefetch_related(
        "access_list",
        "source",
        "tags",
    )


@register_model_view(models.ACLStandardRule, "bulk_delete", path="delete", detail=False)
class ACLStandardRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ACLStandardRule.objects.prefetch_related(
        "access_list",
        "source",
        "tags",
    )
    filterset = filtersets.ACLStandardRuleFilterSet
    table = tables.ACLStandardRuleTable


#
# ACLExtendedRule views
#


@register_model_view(models.ACLExtendedRule)
class ACLExtendedRuleView(generic.ObjectView):
    """
    Defines the view for the ACLExtendedRule django model.
    """

    queryset = models.ACLExtendedRule.objects.prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )


@register_model_view(models.ACLExtendedRule, "list", path="", detail=False)
class ACLExtendedRuleListView(generic.ObjectListView):
    """
    Defines the list view for the ACLExtendedRule django model.
    """

    queryset = models.ACLExtendedRule.objects.prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )
    table = tables.ACLExtendedRuleTable
    filterset = filtersets.ACLExtendedRuleFilterSet
    filterset_form = forms.ACLExtendedRuleFilterForm


@register_model_view(models.ACLExtendedRule, "add", detail=False)
@register_model_view(models.ACLExtendedRule, "edit")
class ACLExtendedRuleEditView(generic.ObjectEditView):
    """
    Defines the edit view for the ACLExtendedRule django model.
    """

    queryset = models.ACLExtendedRule.objects.prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )
    form = forms.ACLExtendedRuleForm

    def get_extra_addanother_params(self, request):
        """
        Returns a dictionary of additional parameters to be passed to the "Add Another" button.
        """

        return {
            "access_list": request.GET.get("access_list") or request.POST.get("access_list"),
        }


@register_model_view(models.ACLExtendedRule, "delete")
class ACLExtendedRuleDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLExtendedRules django model.
    """

    queryset = models.ACLExtendedRule.objects.prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )


@register_model_view(models.ACLExtendedRule, "bulk_delete", path="delete", detail=False)
class ACLExtendedRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ACLExtendedRule.objects.prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )
    filterset = filtersets.ACLExtendedRuleFilterSet
    table = tables.ACLExtendedRuleTable
