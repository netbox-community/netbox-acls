"""Object attributes for the plugin's detail view panels."""

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs

from ..choices import ACLTypeChoices

__all__ = (
    "AssignedObjectAttr",
    "LogOptionsAttr",
    "RuleCountAttr",
)


class AssignedObjectAttr(attrs.GenericForeignKeyAttr):
    """Prefixes an interface assignment with its parent device or virtual machine.

    Renders no ancestors, so the inherited nested argument is inert.
    """

    template_name = "netbox_acls/attrs/assigned_object.html"

    def get_context(self, obj, attr, value, context):
        """Add the target's parent, which only interfaces have."""
        parent = getattr(value, "device", None) or getattr(value, "virtual_machine", None)
        return {**super().get_context(obj, attr, value, context), "parent": parent}


class LogOptionsAttr(attrs.ObjectAttribute):
    """Renders each stored log option as a colored badge."""

    template_name = "netbox_acls/attrs/log_options.html"

    def get_value(self, obj):
        """Return None for an empty list, so render() shows the placeholder."""
        return super().get_value(obj) or None

    def get_context(self, obj, attr, value, context):
        """Return the label and color pairs the template iterates."""
        return {"badges": value}


class RuleCountAttr(attrs.ObjectAttribute):
    """Rule count for an access list, linked to the rule list filtered by that access list."""

    template_name = "netbox_acls/attrs/rule_count.html"
    label = _("Rules")

    RELATIONS = {
        ACLTypeChoices.TYPE_STANDARD: (
            "aclstandardrules",
            "plugins:netbox_acls:aclstandardrule_list",
        ),
        ACLTypeChoices.TYPE_EXTENDED: (
            "aclextendedrules",
            "plugins:netbox_acls:aclextendedrule_list",
        ),
    }

    def __init__(self, accessor="type", **kwargs):
        super().__init__(accessor, **kwargs)

    def get_value(self, obj):
        """Return the rule count of the relation matching the access list's type."""
        relation = self.RELATIONS.get(obj.type)
        return getattr(obj, relation[0]).count() if relation else None

    def get_context(self, obj, attr, value, context):
        """Return the filtered rule list URL. Unreachable when get_value returned None."""
        return {"url": f"{reverse(self.RELATIONS[obj.type][1])}?access_list_id={obj.pk}"}
