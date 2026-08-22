"""
Defines each django model's GUI form to import objects in bulk.
"""

from django.utils.translation import gettext_lazy as _

from netbox.forms import PrimaryModelImportForm
from utilities.forms.fields import CSVChoiceField

from ..choices import ACLActionChoices, ACLFamilyChoices, ACLTypeChoices
from ..models import AccessList

__all__ = ("AccessListImportForm",)


class AccessListImportForm(PrimaryModelImportForm):
    """
    Import form for Access Lists.
    """

    type = CSVChoiceField(
        label=_("Type"),
        choices=ACLTypeChoices,
        help_text=_("Standard rules carry a source only. Extended rules add a destination, protocol and ports."),
    )
    family = CSVChoiceField(
        label=_("Family"),
        choices=ACLFamilyChoices,
        required=False,
        help_text=_("IP family the rules apply to. Defaults to ipv4."),
    )
    default_action = CSVChoiceField(
        label=_("Default action"),
        choices=ACLActionChoices,
        required=False,
        help_text=_("Action taken when no rule matches. Defaults to deny."),
    )

    class Meta:
        model = AccessList
        fields = (
            "name",
            "type",
            "family",
            "default_action",
            "description",
            "owner",
            "comments",
            "tags",
        )
