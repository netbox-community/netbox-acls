"""
Defines each django model's GUI form to import objects in bulk.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelImportForm, OwnerCSVMixin, PrimaryModelImportForm
from utilities.forms.fields import (
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    CSVMultipleChoiceField,
)
from utilities.object_types import object_type_identifier

from ..choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ..constants import (
    ACL_ASSIGNMENT_MODELS,
    ACL_ASSIGNMENT_OBJECT_LOOKUPS,
    ACL_ASSIGNMENT_OBJECT_PARENT_LOOKUPS,
    ACL_RULE_OBJECT_LOOKUPS,
    ACL_RULE_SOURCE_DESTINATION_MODELS,
)
from ..models import AccessList, ACLAssignment, ACLStandardRule

__all__ = (
    "ACLAssignmentImportForm",
    "ACLRuleImportFormMixin",
    "ACLStandardRuleImportForm",
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


class ACLRuleImportFormMixin(forms.Form):
    """
    Columns shared by both rule types.
    """

    action = CSVChoiceField(
        label=_("Action"),
        choices=ACLRuleActionChoices,
        help_text=_("A remark rule carries text only, with no source, destination, protocol or ports."),
    )
    source_type = CSVContentTypeField(
        label=_("Source type (app & model)"),
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        help_text=_("Type of the object the rule matches as its source, as app.model."),
    )
    source = forms.CharField(
        label=_("Source"),
        required=False,
        help_text=_("Prefix, address or aggregate value. IP ranges are addressable by source_id only."),
    )
    source_id = forms.IntegerField(
        label=_("Source ID"),
        required=False,
        help_text=_("Numeric ID of the source object, as an alternative to source."),
    )
    log_options = CSVMultipleChoiceField(
        label=_("Log options"),
        choices=ACLRuleLogOptionChoices,
        required=False,
        help_text=_(
            'Log option values separated by commas, encased with double quotes (e.g. "syslog,cisco-log-input").'
        ),
    )

    object_roles = ("source",)

    def clean(self):
        super().clean()

        for role in self.object_roles:
            self._resolve_object(role)

        return self.cleaned_data

    def _resolve_object(self, role):
        """
        Resolve one role's type and value columns into the object ID the model stores.
        """
        id_field = f"{role}_id"
        object_type = self.cleaned_data.get(f"{role}_type")
        value = self.cleaned_data.get(role)
        object_id = self.cleaned_data.get(id_field)

        if value and object_id:
            raise ValidationError(
                {role: _("{role} and {id_field} are mutually exclusive.").format(role=role, id_field=id_field)},
            )

        if object_type is None:
            if value:
                raise ValidationError(
                    {role: _("{role}_type must be specified when using {role}.").format(role=role)},
                )
            return

        model = object_type.model_class()
        name = model._meta.verbose_name
        lookup = ACL_RULE_OBJECT_LOOKUPS[object_type_identifier(object_type)]

        if not (value or object_id):
            raise ValidationError(
                {role: _("Select a {model}, or give its ID in {id_field}.").format(model=name, id_field=id_field)},
            )

        if value and lookup is None:
            raise ValidationError(
                {
                    role: _("{model} objects have no {role} value. Give the ID in {id_field}.").format(
                        model=name,
                        role=role,
                        id_field=id_field,
                    ),
                },
            )

        if not value:
            return

        try:
            self.cleaned_data[id_field] = model.objects.get(**{lookup: value}).pk
        except model.DoesNotExist:
            raise ValidationError({role: _('{model} "{value}" not found.').format(model=name, value=value)})
        except model.MultipleObjectsReturned:
            raise ValidationError(
                {
                    role: _('Multiple {model} objects match "{value}". Give the ID in {id_field}.').format(
                        model=name,
                        value=value,
                        id_field=id_field,
                    ),
                },
            )


class ACLStandardRuleImportForm(ACLRuleImportFormMixin, PrimaryModelImportForm):
    """
    Import form for Standard ACL Rules.
    """

    access_list = CSVModelChoiceField(
        label=_("Access List"),
        queryset=AccessList.objects.filter(type=ACLTypeChoices.TYPE_STANDARD),
        to_field_name="name",
        help_text=_("Name of a standard access list. Use an access_list.id header to pick one by ID."),
    )

    class Meta:
        model = ACLStandardRule
        # source is the GenericForeignKey's own name, which Django forbids here.
        fields = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "source_type",
            "source_id",
            "log_matches",
            "log_options",
            "description",
            "owner",
            "comments",
            "tags",
        )
