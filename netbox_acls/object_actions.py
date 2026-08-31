"""
Object actions for the plugin's children views.
"""

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.object_actions import AddObject
from utilities.querydict import dict_to_querydict
from utilities.views import get_action_url

__all__ = (
    "AssignACLToAccessList",
    "AssignACLToObject",
)


class AssignACL(AddObject):
    """
    Base Add button for an ACL assignment.

    A children view resolves the inherited permissions_required against its
    child model, so the button asks for the permission of the object it
    creates. url_params mirrors netbox.ui.actions.LinkAction.
    """

    child_model_label = "netbox_acls.ACLAssignment"
    url_params = {}
    label = _("Assign an ACL")
    template_name = "netbox_acls/buttons/assign_acl.html"

    @classmethod
    def get_url(cls, obj):
        """Return the child model's add form, not the viewed object's.

        Never None, so the button template needs no url guard.
        """
        return get_action_url(apps.get_model(cls.child_model_label), action=cls.name)

    @classmethod
    def get_url_params(cls, context):
        """Prefill from the parent, and return to the tab.

        The base copies request.GET, which would carry a filtered tab's query
        string into the form. Only a children view sets a return URL.
        """
        params = {}
        for key, value in cls.url_params.items():
            resolved = value(context) if callable(value) else value
            if resolved is not None:
                params[key] = resolved
        if "return_url" not in params and (return_url := context.get("return_url")):
            params["return_url"] = return_url
        return dict_to_querydict(params)


class AssignACLToAccessList(AssignACL):
    url_params = {"access_list": lambda context: context["object"].pk}


class AssignACLToObject(AssignACL):
    url_params = {
        "assigned_object_content_type": lambda context: ContentType.objects.get_for_model(context["object"]).pk,
        "assigned_object_object_id": lambda context: context["object"].pk,
    }
