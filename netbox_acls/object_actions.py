"""Object actions for the plugin's detail views."""

from urllib.parse import urlencode

from django.apps import apps
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import gettext_lazy as _

from netbox.object_actions import AddObject
from utilities.permissions import get_permission_for_model
from utilities.views import get_action_url

from .choices import ACLTypeChoices

__all__ = ("AddRule",)


class AddRule(AddObject):
    """Add button for the rule type matching an access list's own type."""

    label = _("Add Rule")
    # ObjectView resolves permissions_required against the access list, so the
    # rule permission is checked in render() instead.
    permissions_required = set()

    rule_models = {
        ACLTypeChoices.TYPE_STANDARD: "netbox_acls.ACLStandardRule",
        ACLTypeChoices.TYPE_EXTENDED: "netbox_acls.ACLExtendedRule",
    }
    # Prefilled onto the rule add form. Every key must be a form field.
    url_params_spec = {"access_list": lambda obj: obj.pk}

    @classmethod
    def get_rule_model(cls, obj):
        """Return the rule model matching the access list's type."""
        label = cls.rule_models.get(obj.type)
        return apps.get_model(label) if label else None

    @classmethod
    def get_url(cls, obj):
        """Return the rule add URL, prefilled and returning to the access list."""
        model = cls.get_rule_model(obj)
        if model is None:
            return None
        try:
            url = get_action_url(model, action="add")
        except NoReverseMatch:
            return None
        params = {key: value(obj) for key, value in cls.url_params_spec.items()}
        params["return_url"] = obj.get_absolute_url()
        return f"{url}?{urlencode(params)}"

    @classmethod
    def render(cls, context, obj, **kwargs):
        """Render only for a user permitted to add the matching rule type.

        buttons/add.html has no url guard, so an unresolved URL would
        render href="None" instead of nothing.
        """
        model = cls.get_rule_model(obj)
        if model is None or cls.get_url(obj) is None:
            return ""
        if not context["request"].user.has_perm(get_permission_for_model(model, "add")):
            return ""
        return super().render(context, obj, **kwargs)
