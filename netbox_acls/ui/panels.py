"""Declarative panels for the plugin's detail views."""

from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, attrs
from netbox.ui.panels import ObjectAttributesPanel, ObjectsTablePanel

from .attrs import AssignedObjectAttr, LogOptionsAttr, RuleCountAttr

__all__ = (
    "ACLAssignmentPanel",
    "ACLExtendedRuleDetailsPanel",
    "ACLExtendedRulePanel",
    "ACLRuleLoggingPanel",
    "ACLStandardRuleDetailsPanel",
    "ACLStandardRulePanel",
    "AccessListPanel",
    "RuleTablePanel",
)


class AccessListPanel(ObjectAttributesPanel):
    """Identity attributes of an access list."""

    title = _("Access List")

    type = attrs.ChoiceAttr("type", label=_("Type"))
    family = attrs.ChoiceAttr("family", label=_("Family"))
    default_action = attrs.ChoiceAttr("default_action", label=_("Default Action"))
    rules = RuleCountAttr()
    description = attrs.TextAttr("description", label=_("Description"))


class RuleTablePanel(ObjectsTablePanel):
    """Rules of one type, shown only on an access list of that type."""

    def __init__(self, acl_type, model, title):
        self.acl_type = acl_type
        super().__init__(
            model,
            filters={"access_list_id": lambda context: context["object"].pk},
            exclude_columns=["access_list"],
            include_columns=["log_matches", "log_options_list"],
            title=title,
            actions=[
                actions.AddObject(
                    model,
                    url_params={"access_list": lambda context: context["object"].pk},
                    label=_("Add Rule"),
                ),
            ],
        )

    def should_render(self, context):
        """Render only on an access list whose type matches these rules."""
        access_list = context.get("object")
        if access_list is None or access_list.type != self.acl_type:
            return False
        return super().should_render(context)


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
    """Match criteria of a standard ACL rule."""

    title = _("Details")

    action = attrs.ChoiceAttr("action", label=_("Action"))
    remark = attrs.TextAttr("remark", label=_("Remark"))
    source = attrs.GenericForeignKeyAttr("source", linkify=True, label=_("Source"))


class ACLExtendedRulePanel(ACLStandardRulePanel):
    """Identity attributes of an extended ACL rule."""

    title = _("ACL Extended Rule")


class ACLExtendedRuleDetailsPanel(ObjectAttributesPanel):
    """Match criteria of an extended ACL rule.

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


class ACLRuleLoggingPanel(ObjectAttributesPanel):
    """Logging controls of an ACL rule, shared by both rule types."""

    title = _("Logging")

    log_matches = attrs.BooleanAttr("log_matches", label=_("Log Matches"))
    log_options = LogOptionsAttr("log_options_badges", label=_("Log Options"))
