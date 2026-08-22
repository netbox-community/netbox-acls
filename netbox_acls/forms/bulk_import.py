"""
Defines each django model's GUI form to import objects in bulk.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelImportForm, OwnerCSVMixin, PrimaryModelImportForm
from utilities.forms.fields import CSVChoiceField, CSVContentTypeField, CSVModelChoiceField
from utilities.object_types import object_type_identifier

from ..choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ..constants import (
    ACL_ASSIGNMENT_MODELS,
    ACL_ASSIGNMENT_OBJECT_LOOKUPS,
    ACL_ASSIGNMENT_OBJECT_PARENT_LOOKUPS,
)
from ..models import AccessList, ACLAssignment

__all__ = (
    "ACLAssignmentImportForm",
    "AccessListImportForm",
)


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


class ACLAssignmentImportForm(OwnerCSVMixin, NetBoxModelImportForm):
    """
    Import form for ACL Assignments.
    """

    access_list = CSVModelChoiceField(
        label=_("Access List"),
        queryset=AccessList.objects.all(),
        to_field_name="name",
        help_text=_("Access list name. Names are not unique, so use an access_list.id header to pick one by ID."),
    )
    assigned_object_type = CSVContentTypeField(
        label=_("Assigned object type (app & model)"),
        queryset=ContentType.objects.filter(ACL_ASSIGNMENT_MODELS),
        help_text=_("Type of the object the access list is assigned to, as app.model."),
    )
    assigned_object = forms.CharField(
        label=_("Assigned object"),
        required=False,
        help_text=_("Name of the assigned object. Give assigned_object_parent as well when the name repeats."),
    )
    assigned_object_parent = forms.CharField(
        label=_("Assigned object parent"),
        required=False,
        help_text=_("Name of the device or virtual machine carrying the assigned interface."),
    )
    # The model field is non-null, so the generated field would reject every row using a name.
    assigned_object_id = forms.IntegerField(
        label=_("Assigned object ID"),
        required=False,
        help_text=_("Numeric ID of the assigned object, as an alternative to assigned_object."),
    )
    direction = CSVChoiceField(
        label=_("Direction"),
        choices=ACLAssignmentDirectionChoices,
        help_text=_("Device, virtual chassis and virtual machine assignments are always stored as none."),
    )

    class Meta:
        model = ACLAssignment
        # assigned_object is the GenericForeignKey's own name, which Django forbids here.
        fields = (
            "access_list",
            "assigned_object_type",
            "assigned_object_parent",
            "assigned_object_id",
            "direction",
            "owner",
            "comments",
            "tags",
        )

    def clean(self):
        super().clean()

        object_type = self.cleaned_data.get("assigned_object_type")
        name = self.cleaned_data.get("assigned_object")
        parent = self.cleaned_data.get("assigned_object_parent")
        object_id = self.cleaned_data.get("assigned_object_id")

        if name and object_id:
            raise ValidationError(
                {"assigned_object": _("assigned_object and assigned_object_id are mutually exclusive.")},
            )

        # BulkImportView drops the columns an update row omits, leaving the stored relation alone.
        if object_type is None:
            if name or parent:
                raise ValidationError(
                    {"assigned_object": _("assigned_object_type must be specified when using assigned_object.")},
                )
            return self.cleaned_data

        model = object_type.model_class()
        label = object_type_identifier(object_type)
        parent_lookup = ACL_ASSIGNMENT_OBJECT_PARENT_LOOKUPS.get(label)

        if not (name or object_id):
            raise ValidationError(
                {
                    "assigned_object": _("Select a {model}, or give its ID in assigned_object_id.").format(
                        model=model._meta.verbose_name,
                    ),
                },
            )

        if parent and not parent_lookup:
            raise ValidationError(
                {
                    "assigned_object_parent": _("{model} objects have no parent qualifier.").format(
                        model=model._meta.verbose_name,
                    ),
                },
            )

        if not name:
            return self.cleaned_data

        query = {ACL_ASSIGNMENT_OBJECT_LOOKUPS[label]: name}
        if parent:
            query[parent_lookup] = parent

        try:
            self.cleaned_data["assigned_object_id"] = model.objects.get(**query).pk
        except model.DoesNotExist:
            raise ValidationError(
                {
                    "assigned_object": _('{model} "{name}" not found.').format(
                        model=model._meta.verbose_name,
                        name=name,
                    ),
                },
            )
        except model.MultipleObjectsReturned:
            raise ValidationError(
                {
                    "assigned_object": _(
                        'Multiple {model} objects match "{name}". Give the ID in assigned_object_id.'
                    ).format(model=model._meta.verbose_name, name=name),
                },
            )

        return self.cleaned_data
