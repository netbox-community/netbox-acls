"""
Defines each django model's GUI form to import objects in bulk.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelImportForm, OwnerCSVMixin, PrimaryModelImportForm
from utilities.forms.fields import (
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    CSVMultipleChoiceField,
    NumericRangeArrayField,
)
from utilities.object_types import object_type_identifier

from ..choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
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
from ..models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule

__all__ = (
    "ACLAssignmentImportForm",
    "ACLExtendedRuleImportForm",
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
        help_texts = {
            "name": _("Name of the access list. Letters, numbers, underscores and hyphens only."),
        }


class ObjectImportMixin(forms.Form):
    """
    Resolve <role>_type plus a value column into the <role>_id the model stores.

    The value column is plain text and is resolved in clean(), so nothing depends on the
    row's content type at build time.
    """

    object_roles: tuple = ()
    # role -> {content type: field the value is looked up by, or None when ID only}
    object_lookups: dict = {}
    # role -> {content type: query path to the parent that makes the value unique}
    object_parents: dict = {}

    def clean(self):
        super().clean()

        for role in self.object_roles:
            self._resolve_object(role)

        return self.cleaned_data

    def _error_field(self, *candidates):
        """
        Pick the first column the row still carries, since add_error rejects a deleted one.
        """
        return next((name for name in candidates if name in self.fields), NON_FIELD_ERRORS)

    def _resolve_object(self, role):
        """
        Resolve one role's columns into the object ID the model stores.
        """
        type_field, id_field = f"{role}_type", f"{role}_id"
        parent_field = f"{role}_parent"
        object_type = self.cleaned_data.get(type_field)
        value = self.cleaned_data.get(role)
        object_id = self.cleaned_data.get(id_field)
        parent = self.cleaned_data.get(parent_field)

        if value and object_id:
            raise ValidationError(
                {role: _("{role} and {id_field} are mutually exclusive.").format(role=role, id_field=id_field)},
            )

        if object_id and parent:
            raise ValidationError(
                {
                    parent_field: _("{parent_field} qualifies {role}, so it cannot be given with {id_field}.").format(
                        parent_field=parent_field,
                        role=role,
                        id_field=id_field,
                    ),
                },
            )

        # BulkImportView drops the columns an update row omits, leaving the stored relation alone.
        if object_type is None:
            # A supplied but unresolvable type has already reported itself.
            if self.data.get(type_field):
                return
            if value or parent:
                raise ValidationError(
                    {
                        self._error_field(role, parent_field): _(
                            "{type_field} must be specified when using {role}."
                        ).format(type_field=type_field, role=role),
                    },
                )
            if object_id and type_field in self.fields:
                raise ValidationError(
                    {
                        type_field: _("{type_field} must be specified when using {id_field}.").format(
                            type_field=type_field,
                            id_field=id_field,
                        ),
                    },
                )
            return

        model = object_type.model_class()
        name = model._meta.verbose_name
        label = object_type_identifier(object_type)
        lookup = self.object_lookups[role][label]
        parent_lookup = self.object_parents.get(role, {}).get(label)

        if not (value or object_id):
            raise ValidationError(
                {
                    self._error_field(role, type_field): _("Select a {model}, or give its ID in {id_field}.").format(
                        model=name, id_field=id_field
                    ),
                },
            )

        if parent and not parent_lookup:
            raise ValidationError(
                {parent_field: _("{model} objects have no parent qualifier.").format(model=name)},
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

        query = {lookup: value}
        if parent:
            query[parent_lookup] = parent

        try:
            self.cleaned_data[id_field] = model.objects.get(**query).pk
        except model.DoesNotExist:
            if parent:
                message = _('{model} "{value}" not found on "{parent}".').format(
                    model=name,
                    value=value,
                    parent=parent,
                )
            else:
                message = _('{model} "{value}" not found.').format(model=name, value=value)
            raise ValidationError({role: message})
        except ValidationError as error:
            raise ValidationError({role: error.messages[0]})
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


class ACLAssignmentImportForm(ObjectImportMixin, OwnerCSVMixin, NetBoxModelImportForm):
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
        help_text=_(
            "Device, virtual chassis and virtual machine assignments are always stored as none. "
            "Interface assignments require ingress or egress."
        ),
    )

    object_roles = ("assigned_object",)
    object_lookups = {"assigned_object": ACL_ASSIGNMENT_OBJECT_LOOKUPS}
    object_parents = {"assigned_object": ACL_ASSIGNMENT_OBJECT_PARENT_LOOKUPS}

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


class ACLRuleImportFormMixin(ObjectImportMixin):
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
        help_text=_(
            "Prefix, address or aggregate value, for example 10.0.0.0/8. IP ranges are addressable by source_id only."
        ),
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
            "Log option values separated by commas, encased with double quotes "
            '(e.g. "syslog,cisco-log-input"). Requires log_matches.'
        ),
    )

    object_roles = ("source",)
    object_lookups = {"source": ACL_RULE_OBJECT_LOOKUPS}


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
        help_texts = {
            "sequence": _("Rule order within the access list. Never assigned automatically on import."),
        }


class ACLExtendedRuleImportForm(ACLRuleImportFormMixin, PrimaryModelImportForm):
    """
    Import form for Extended ACL Rules.
    """

    access_list = CSVModelChoiceField(
        label=_("Access List"),
        queryset=AccessList.objects.filter(type=ACLTypeChoices.TYPE_EXTENDED),
        to_field_name="name",
        help_text=_("Name of an extended access list. Use an access_list.id header to pick one by ID."),
    )
    protocol = CSVChoiceField(
        label=_("Protocol"),
        choices=ACLProtocolChoices,
        required=False,
        help_text=_("Port ranges apply to tcp and udp only."),
    )
    source_port_ranges = NumericRangeArrayField(required=False)
    destination_type = CSVContentTypeField(
        label=_("Destination type (app & model)"),
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        help_text=_("Type of the object the rule matches as its destination, as app.model."),
    )
    destination = forms.CharField(
        label=_("Destination"),
        required=False,
        help_text=_(
            "Prefix, address or aggregate value, for example 10.0.0.0/8. "
            "IP ranges are addressable by destination_id only."
        ),
    )
    destination_id = forms.IntegerField(
        label=_("Destination ID"),
        required=False,
        help_text=_("Numeric ID of the destination object, as an alternative to destination."),
    )
    destination_port_ranges = NumericRangeArrayField(required=False)

    object_roles = ("source", "destination")
    object_lookups = {
        "source": ACL_RULE_OBJECT_LOOKUPS,
        "destination": ACL_RULE_OBJECT_LOOKUPS,
    }

    class Meta:
        model = ACLExtendedRule
        # source and destination are the GenericForeignKey names, which Django forbids here.
        fields = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "protocol",
            "source_type",
            "source_id",
            "source_port_ranges",
            "destination_type",
            "destination_id",
            "destination_port_ranges",
            "log_matches",
            "log_options",
            "description",
            "owner",
            "comments",
            "tags",
        )
        help_texts = {
            "sequence": _("Rule order within the access list. Never assigned automatically on import."),
        }
