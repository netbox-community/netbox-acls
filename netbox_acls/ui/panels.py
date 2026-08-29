"""Declarative panels for the plugin's detail views."""

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.panels import ContextTablePanel, ObjectAttributesPanel

from .attrs import AssignedObjectAttr, LogOptionsAttr, RuleCountAttr

__all__ = (
    "ACLAssignmentPanel",
    "ACLExtendedRuleDetailsPanel",
    "ACLExtendedRulePanel",
    "ACLStandardRuleDetailsPanel",
    "ACLStandardRulePanel",
    "AccessListPanel",
    "AccessListRulesPanel",
)


class AccessListPanel(ObjectAttributesPanel):
    """Identity attributes of an access list."""

    title = _("Access List")

    type = attrs.ChoiceAttr("type", label=_("Type"))
    family = attrs.ChoiceAttr("family", label=_("Family"))
    default_action = attrs.ChoiceAttr("default_action", label=_("Default Action"))
    rules = RuleCountAttr()
    description = attrs.TextAttr("description", label=_("Description"))


class AccessListRulesPanel(ContextTablePanel):
    """Rules table for an access list, titled for the list's type."""

    def __init__(self, **kwargs):
        super().__init__("rules_table", **kwargs)

    def get_context(self, context):
        """Title the card for the access list's own type."""
        panel_context = super().get_context(context)
        panel_context["title"] = _("%(type)s Rules") % {
            "type": panel_context["object"].get_type_display(),
        }
        return panel_context


class ACLAssignmentPanel(ObjectAttributesPanel):
    """Identity attributes of an ACL assignment."""

    title = _("ACL Assignment")

    access_list = attrs.RelatedObjectAttr("access_list", linkify=True, label=_("Access List"))
    assigned_object = AssignedObjectAttr("assigned_object", linkify=True, label=_("Assigned Object"))
    direction = attrs.ChoiceAttr("direction", label=_("Direction"))


class ACLStandardRulePanel(ObjectAttributesPanel):
    """Identity attributes of a standard ACL rule."""

    title = _("ACL Standard Rule")

    access_list = attrs.RelatedObjectAttr("access_list", linkify=True, label=_("Access List"))
    sequence = attrs.NumericAttr("sequence", label=_("Sequence"))
    description = attrs.TextAttr("description", label=_("Description"))


class ACLStandardRuleDetailsPanel(ObjectAttributesPanel):
    """Match criteria and logging of a standard ACL rule."""

    title = _("Details")

    action = attrs.ChoiceAttr("action", label=_("Action"))
    remark = attrs.TextAttr("remark", label=_("Remark"))
    source = attrs.GenericForeignKeyAttr("source", linkify=True, label=_("Source"))
    log_matches = attrs.BooleanAttr("log_matches", label=_("Log Matches"))
    log_options = LogOptionsAttr("log_options_badges", label=_("Log Options"))


class ACLExtendedRulePanel(ACLStandardRulePanel):
    """Identity attributes of an extended ACL rule."""

    title = _("ACL Extended Rule")


class ACLExtendedRuleDetailsPanel(ObjectAttributesPanel):
    """Match criteria and logging of an extended ACL rule.

    Declares every attribute rather than extending the standard panel,
    since the metaclass places inherited attributes before local ones
    and the extended fields interleave with them.
    """

    title = _("Details")

    action = attrs.ChoiceAttr("action", label=_("Action"))
    remark = attrs.TextAttr("remark", label=_("Remark"))
    protocol = attrs.ChoiceAttr("protocol", label=_("Protocol"))
    source = attrs.GenericForeignKeyAttr("source", linkify=True, label=_("Source"))
    source_port_ranges = attrs.ArrayAttr("source_port_ranges_list", label=_("Source Port Ranges"))
    destination = attrs.GenericForeignKeyAttr("destination", linkify=True, label=_("Destination"))
    destination_port_ranges = attrs.ArrayAttr(
        "destination_port_ranges_list",
        label=_("Destination Port Ranges"),
    )
    log_matches = attrs.BooleanAttr("log_matches", label=_("Log Matches"))
    log_options = LogOptionsAttr("log_options_badges", label=_("Log Options"))
