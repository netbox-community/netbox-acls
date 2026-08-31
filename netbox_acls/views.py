"""
Defines the business logic for the plugin.
Specifically, all the various interactions with a client.
"""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, CharField, Count, Q, Value, When
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, VirtualChassis
from extras.ui.panels import CustomFieldsPanel, TagsPanel
from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.object_actions import AddObject, BulkDelete, BulkEdit, BulkExport
from netbox.ui import layout
from netbox.ui.breadcrumbs import Breadcrumb, filtered_list_url
from netbox.ui.panels import CommentsPanel
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from virtualization.models import VirtualMachine, VMInterface

from . import choices, filtersets, forms, models, object_actions, tables, ui

__all__ = (
    "ACLAssignmentBulkDeleteView",
    "ACLAssignmentDeleteView",
    "ACLAssignmentEditView",
    "ACLAssignmentListView",
    "ACLAssignmentView",
    "ACLExtendedRuleBulkDeleteView",
    "ACLExtendedRuleDeleteView",
    "ACLExtendedRuleEditView",
    "ACLExtendedRuleListView",
    "ACLExtendedRuleView",
    "ACLStandardRuleBulkDeleteView",
    "ACLStandardRuleDeleteView",
    "ACLStandardRuleEditView",
    "ACLStandardRuleListView",
    "ACLStandardRuleView",
    "AccessListBulkDeleteView",
    "AccessListDeleteView",
    "AccessListEditView",
    "AccessListListView",
    "AccessListView",
)


class ACLRuleSequenceMixin:
    """
    Mixin that auto-assigns the next available sequence number to new ACL rules.

    Used with ObjectEditView to pre-populate the sequence field when creating
    rules via the "Add" form (not clone/add-another, which preserves sequence).
    """

    def alter_object(self, obj, request, url_args, url_kwargs):
        obj = super().alter_object(obj, request, url_args, url_kwargs)

        # Skip if editing an existing object or sequence already provided (clone/add-another)
        if obj.pk or "sequence" in request.GET:
            return obj

        # Parse access_list ID; bail out gracefully if missing/invalid.
        # Not str.isdigit(): it accepts superscript digits that int() then rejects.
        try:
            access_list_id = int(request.GET.get("access_list", ""))
        except ValueError:
            return obj

        obj.sequence = obj.__class__.objects.get_next_sequence(access_list_id)
        return obj


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
    actions = (object_actions.AssignACLToObject, BulkExport, BulkDelete)

    def get_children(self, request, parent):
        """
        Return all objects of ACLAssignment.
        """
        return (
            models.ACLAssignment.objects.restrict(request.user, "view")
            .select_related("owner")
            .prefetch_related(
                "access_list",
                "assigned_object_type",
                "assigned_object",
                "tags",
            )
        )


def rule_reference_filter(instance, *roles):
    """
    Return a Q matching rules whose named generic FK roles point at the instance.
    """
    # An empty Q matches every row, so a role-less call must not be silently accepted.
    if not roles:
        raise ValueError("rule_reference_filter() requires at least one role.")

    content_type = ContentType.objects.get_for_model(instance)
    query = Q()
    for role in roles:
        query |= Q(**{f"{role}_type": content_type, f"{role}_id": instance.pk})
    return query


class ACLStandardRuleChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of referencing ACL Standard Rules."""

    child_model = models.ACLStandardRule
    filterset = filtersets.ACLStandardRuleFilterSet
    tab = ViewTab(
        label=_("ACL Standard Rules"),
        badge=lambda obj: models.ACLStandardRule.objects.filter(
            rule_reference_filter(obj, "source"),
        ).count(),
        permission="netbox_acls.view_aclstandardrule",
        weight=1100,
        hide_if_empty=True,
    )
    table = tables.ACLStandardRuleTable
    # Read-only tab. ObjectChildrenView has no export handler, and editing a rule belongs
    # on the rule itself.
    actions = ()

    def get_children(self, request, parent):
        """Return the standard rules whose source is the parent object."""
        return (
            models.ACLStandardRule.objects.restrict(request.user, "view")
            .filter(rule_reference_filter(parent, "source"))
            .select_related("owner")
            .prefetch_related("access_list", "source", "tags")
        )

    def get_table(self, *args, **kwargs):
        """Return the table with the source columns hidden."""
        table = super().get_table(*args, **kwargs)

        # Every row's source is the parent object. Visibility is set after configure(),
        # which resets columns from the user's preference or the table defaults.
        table.columns.hide("source")
        table.columns.hide("source_type")

        return table


class ACLExtendedRuleChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of referencing ACL Extended Rules."""

    child_model = models.ACLExtendedRule
    filterset = filtersets.ACLExtendedRuleFilterSet
    tab = ViewTab(
        label=_("ACL Extended Rules"),
        badge=lambda obj: models.ACLExtendedRule.objects.filter(
            rule_reference_filter(obj, "source", "destination"),
        ).count(),
        permission="netbox_acls.view_aclextendedrule",
        weight=1200,
        hide_if_empty=True,
    )
    table = tables.ACLExtendedRuleUsageTable
    # Read-only tab, as on the standard rule base.
    actions = ()

    def get_children(self, request, parent):
        """Return the extended rules referencing the parent at either end."""
        source = rule_reference_filter(parent, "source")
        destination = rule_reference_filter(parent, "destination")

        # Both ends live on the rule's own row, so the OR needs no distinct().
        return (
            models.ACLExtendedRule.objects.restrict(request.user, "view")
            .filter(source | destination)
            .annotate(
                used_as=Case(
                    When(source & destination, then=Value(choices.ACLRuleUsageChoices.USAGE_BOTH)),
                    When(source, then=Value(choices.ACLRuleUsageChoices.USAGE_SOURCE)),
                    When(destination, then=Value(choices.ACLRuleUsageChoices.USAGE_DESTINATION)),
                    default=Value(""),
                    output_field=CharField(),
                ),
            )
            .select_related("owner")
            .prefetch_related("access_list", "source", "destination", "tags")
        )


#
# AccessList views
#


@register_model_view(models.AccessList)
class AccessListView(generic.ObjectView):
    """
    Defines the view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.select_related("owner").prefetch_related("tags")
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        left_panels=[
            ui.AccessListPanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
        bottom_panels=[
            ui.RuleTablePanel(
                choices.ACLTypeChoices.TYPE_STANDARD,
                "netbox_acls.aclstandardrule",
                _("Standard Rules"),
            ),
            ui.RuleTablePanel(
                choices.ACLTypeChoices.TYPE_EXTENDED,
                "netbox_acls.aclextendedrule",
                _("Extended Rules"),
            ),
        ],
    )


@register_model_view(models.AccessList, "list", path="", detail=False)
class AccessListListView(generic.ObjectListView):
    """
    Defines the list view for the AccessLists django model.
    """

    queryset = (
        models.AccessList.objects.annotate(
            rule_count=Count("aclextendedrules") + Count("aclstandardrules"),
        )
        .select_related("owner")
        .prefetch_related("tags")
    )
    table = tables.AccessListTable
    filterset = filtersets.AccessListFilterSet
    filterset_form = forms.AccessListFilterForm
    actions = (AddObject, BulkEdit, BulkExport, BulkDelete)


@register_model_view(models.AccessList, "add", detail=False)
@register_model_view(models.AccessList, "edit")
class AccessListEditView(generic.ObjectEditView):
    """
    Defines the edit view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.select_related("owner").prefetch_related("tags")
    form = forms.AccessListForm


@register_model_view(models.AccessList, "delete")
class AccessListDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the AccessLists django model.
    """

    queryset = models.AccessList.objects.select_related("owner").prefetch_related("tags")


@register_model_view(models.AccessList, "bulk_edit", path="edit", detail=False)
class AccessListBulkEditView(generic.BulkEditView):
    """
    Bulk edit view for editing multiple objects of AccessLists.
    """

    queryset = models.AccessList.objects.all()
    filterset = filtersets.AccessListFilterSet
    table = tables.AccessListTable
    form = forms.AccessListBulkEditForm


@register_model_view(models.AccessList, "bulk_delete", path="delete", detail=False)
class AccessListBulkDeleteView(generic.BulkDeleteView):
    """
    Bulk delete view for deleting multiple objects of AccessLists.
    """

    queryset = models.AccessList.objects.select_related("owner").prefetch_related("tags")
    filterset = filtersets.AccessListFilterSet
    table = tables.AccessListTable


@register_model_view(models.AccessList, "aclassignments", path="assignments")
class AccessListACLAssignmentView(ACLAssignmentChildrenView):
    """
    Children view of ACL Assignment of AccessLists.
    """

    queryset = models.AccessList.objects.all()
    tab = ViewTab(
        label=_("Assignments"),
        badge=lambda obj: obj.aclassignments.count(),
        permission="netbox_acls.view_aclassignment",
        weight=1100,
    )
    actions = (object_actions.AssignACLToAccessList, BulkExport, BulkDelete)

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(access_list=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with the assigned object colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide the access list column
        table.columns.hide("access_list")
        # Hide the type column
        table.columns.hide("type")
        # Hide the default action column
        table.columns.hide("default_action")

        return table


#
# ACLAssignment views
#


@register_model_view(models.ACLAssignment)
class ACLAssignmentView(generic.ObjectView):
    """
    Defines the view for the ACLAssignments django model.
    """

    queryset = models.ACLAssignment.objects.select_related("owner").prefetch_related(
        "access_list",
        "assigned_object",
        "tags",
    )
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        left_panels=[
            ui.ACLAssignmentPanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
        breadcrumbs=[
            Breadcrumb(
                "access_list",
                url=filtered_list_url("plugins:netbox_acls:aclassignment_list", "access_list_id"),
            ),
        ],
    )


@register_model_view(models.ACLAssignment, "list", path="", detail=False)
class ACLAssignmentListView(generic.ObjectListView):
    """
    Defines the list view for the ACLAssignments django model.
    """

    queryset = models.ACLAssignment.objects.select_related("owner").prefetch_related(
        "access_list",
        "assigned_object",
        "tags",
    )
    table = tables.ACLAssignmentTable
    filterset = filtersets.ACLAssignmentFilterSet
    filterset_form = forms.ACLAssignmentFilterForm
    actions = (AddObject, BulkEdit, BulkExport, BulkDelete)


@register_model_view(models.ACLAssignment, "add", detail=False)
@register_model_view(models.ACLAssignment, "edit")
class ACLAssignmentEditView(generic.ObjectEditView):
    """
    Defines the edit view for the ACLAssignments django model.
    """

    queryset = models.ACLAssignment.objects.select_related("owner").prefetch_related(
        "access_list",
        "assigned_object",
        "tags",
    )
    form = forms.ACLAssignmentForm


@register_model_view(models.ACLAssignment, "delete")
class ACLAssignmentDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLAssignments django model.
    """

    queryset = models.ACLAssignment.objects.select_related("owner").prefetch_related(
        "access_list",
        "assigned_object",
        "tags",
    )


@register_model_view(models.ACLAssignment, "bulk_edit", path="edit", detail=False)
class ACLAssignmentBulkEditView(generic.BulkEditView):
    """
    Bulk edit view for editing multiple objects of ACLAssignments.
    """

    queryset = models.ACLAssignment.objects.all()
    filterset = filtersets.ACLAssignmentFilterSet
    table = tables.ACLAssignmentTable
    form = forms.ACLAssignmentBulkEditForm


@register_model_view(models.ACLAssignment, "bulk_delete", path="delete", detail=False)
class ACLAssignmentBulkDeleteView(generic.BulkDeleteView):
    """
    Bulk delete view for deleting multiple objects of ACLAssignments.
    """

    queryset = models.ACLAssignment.objects.select_related("owner").prefetch_related(
        "access_list",
        "assigned_object",
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
    Children view of ACL Assignment of VirtualChassis.
    """

    queryset = VirtualChassis.objects.all()

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

    queryset = models.ACLStandardRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "tags",
    )
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        left_panels=[
            ui.ACLStandardRulePanel(),
            ui.ACLStandardRuleDetailsPanel(),
            ui.ACLRuleLoggingPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            TagsPanel(),
            CommentsPanel(),
        ],
        breadcrumbs=[
            Breadcrumb(
                "access_list",
                url=filtered_list_url("plugins:netbox_acls:aclstandardrule_list", "access_list_id"),
            ),
        ],
    )


@register_model_view(models.ACLStandardRule, "list", path="", detail=False)
class ACLStandardRuleListView(generic.ObjectListView):
    """
    Defines the list view for the ACLStandardRule django model.
    """

    queryset = models.ACLStandardRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "tags",
    )
    table = tables.ACLStandardRuleTable
    filterset = filtersets.ACLStandardRuleFilterSet
    filterset_form = forms.ACLStandardRuleFilterForm
    actions = (AddObject, BulkEdit, BulkExport, BulkDelete)


@register_model_view(models.ACLStandardRule, "add", detail=False)
@register_model_view(models.ACLStandardRule, "edit")
class ACLStandardRuleEditView(ACLRuleSequenceMixin, generic.ObjectEditView):
    """
    Defines the edit view for the ACLStandardRule django model.
    """

    queryset = models.ACLStandardRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "tags",
    )
    form = forms.ACLStandardRuleForm


@register_model_view(models.ACLStandardRule, "delete")
class ACLStandardRuleDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLStandardRules django model.
    """

    queryset = models.ACLStandardRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "tags",
    )


@register_model_view(models.ACLStandardRule, "bulk_edit", path="edit", detail=False)
class ACLStandardRuleBulkEditView(generic.BulkEditView):
    """
    Bulk edit view for editing multiple objects of ACLStandardRules.
    """

    queryset = models.ACLStandardRule.objects.all()
    filterset = filtersets.ACLStandardRuleFilterSet
    table = tables.ACLStandardRuleTable
    form = forms.ACLStandardRuleBulkEditForm


@register_model_view(models.ACLStandardRule, "bulk_delete", path="delete", detail=False)
class ACLStandardRuleBulkDeleteView(generic.BulkDeleteView):
    """
    Bulk delete view for deleting multiple objects of ACLStandardRules.
    """

    queryset = models.ACLStandardRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "tags",
    )
    filterset = filtersets.ACLStandardRuleFilterSet
    table = tables.ACLStandardRuleTable


@register_model_view(Aggregate, "aclstandardrules", path="acl-standard-rules")
class AggregateACLStandardRuleView(ACLStandardRuleChildrenView):
    """
    Children view of ACL Standard Rules referencing an Aggregate.
    """

    queryset = Aggregate.objects.all()


@register_model_view(IPAddress, "aclstandardrules", path="acl-standard-rules")
class IPAddressACLStandardRuleView(ACLStandardRuleChildrenView):
    """
    Children view of ACL Standard Rules referencing an IP Address.
    """

    queryset = IPAddress.objects.all()


@register_model_view(IPRange, "aclstandardrules", path="acl-standard-rules")
class IPRangeACLStandardRuleView(ACLStandardRuleChildrenView):
    """
    Children view of ACL Standard Rules referencing an IP Range.
    """

    queryset = IPRange.objects.all()


@register_model_view(Prefix, "aclstandardrules", path="acl-standard-rules")
class PrefixACLStandardRuleView(ACLStandardRuleChildrenView):
    """
    Children view of ACL Standard Rules referencing a Prefix.
    """

    queryset = Prefix.objects.all()


#
# ACLExtendedRule views
#


@register_model_view(models.ACLExtendedRule)
class ACLExtendedRuleView(generic.ObjectView):
    """
    Defines the view for the ACLExtendedRule django model.
    """

    queryset = models.ACLExtendedRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        left_panels=[
            ui.ACLExtendedRulePanel(),
            ui.ACLExtendedRuleDetailsPanel(),
            ui.ACLRuleLoggingPanel(),
        ],
        right_panels=[
            CustomFieldsPanel(),
            TagsPanel(),
            CommentsPanel(),
        ],
        breadcrumbs=[
            Breadcrumb(
                "access_list",
                url=filtered_list_url("plugins:netbox_acls:aclextendedrule_list", "access_list_id"),
            ),
        ],
    )


@register_model_view(models.ACLExtendedRule, "list", path="", detail=False)
class ACLExtendedRuleListView(generic.ObjectListView):
    """
    Defines the list view for the ACLExtendedRule django model.
    """

    queryset = models.ACLExtendedRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )
    table = tables.ACLExtendedRuleTable
    filterset = filtersets.ACLExtendedRuleFilterSet
    filterset_form = forms.ACLExtendedRuleFilterForm
    actions = (AddObject, BulkEdit, BulkExport, BulkDelete)


@register_model_view(models.ACLExtendedRule, "add", detail=False)
@register_model_view(models.ACLExtendedRule, "edit")
class ACLExtendedRuleEditView(ACLRuleSequenceMixin, generic.ObjectEditView):
    """
    Defines the edit view for the ACLExtendedRule django model.
    """

    queryset = models.ACLExtendedRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )
    form = forms.ACLExtendedRuleForm


@register_model_view(models.ACLExtendedRule, "delete")
class ACLExtendedRuleDeleteView(generic.ObjectDeleteView):
    """
    Defines delete view for the ACLExtendedRules django model.
    """

    queryset = models.ACLExtendedRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )


@register_model_view(models.ACLExtendedRule, "bulk_edit", path="edit", detail=False)
class ACLExtendedRuleBulkEditView(generic.BulkEditView):
    """
    Bulk edit view for editing multiple objects of ACLExtendedRules.
    """

    queryset = models.ACLExtendedRule.objects.all()
    filterset = filtersets.ACLExtendedRuleFilterSet
    table = tables.ACLExtendedRuleTable
    form = forms.ACLExtendedRuleBulkEditForm


@register_model_view(models.ACLExtendedRule, "bulk_delete", path="delete", detail=False)
class ACLExtendedRuleBulkDeleteView(generic.BulkDeleteView):
    """
    Bulk delete view for deleting multiple objects of ACLExtendedRules.
    """

    queryset = models.ACLExtendedRule.objects.select_related("owner").prefetch_related(
        "access_list",
        "source",
        "destination",
        "tags",
    )
    filterset = filtersets.ACLExtendedRuleFilterSet
    table = tables.ACLExtendedRuleTable


@register_model_view(Aggregate, "aclextendedrules", path="acl-extended-rules")
class AggregateACLExtendedRuleView(ACLExtendedRuleChildrenView):
    """
    Children view of ACL Extended Rules referencing an Aggregate.
    """

    queryset = Aggregate.objects.all()


@register_model_view(IPAddress, "aclextendedrules", path="acl-extended-rules")
class IPAddressACLExtendedRuleView(ACLExtendedRuleChildrenView):
    """
    Children view of ACL Extended Rules referencing an IP Address.
    """

    queryset = IPAddress.objects.all()


@register_model_view(IPRange, "aclextendedrules", path="acl-extended-rules")
class IPRangeACLExtendedRuleView(ACLExtendedRuleChildrenView):
    """
    Children view of ACL Extended Rules referencing an IP Range.
    """

    queryset = IPRange.objects.all()


@register_model_view(Prefix, "aclextendedrules", path="acl-extended-rules")
class PrefixACLExtendedRuleView(ACLExtendedRuleChildrenView):
    """
    Children view of ACL Extended Rules referencing a Prefix.
    """

    queryset = Prefix.objects.all()
