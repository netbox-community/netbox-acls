"""
Defines each django model's GUI form to edit multiple objects at once.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from dcim.models import Interface
from netbox.forms import NetBoxModelBulkEditForm, PrimaryModelBulkEditForm
from netbox.forms.mixins import OwnerMixin
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    GenericObjectChoiceField,
    NumericRangeArrayField,
)
from utilities.forms.mixins import GenericObjectFormMixin
from utilities.forms.rendering import FieldSet
from utilities.forms.utils import add_blank_choice
from utilities.forms.widgets import BulkEditNullBooleanSelect
from virtualization.models import VMInterface

from ..choices import (
    ACLActionChoices,
    ACLAssignmentDirectionUIChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ..constants import ACL_ASSIGNMENT_MODELS, ACL_RULE_SOURCE_DESTINATION_MODELS
from ..models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule
from ..models.access_list_rules import (
    ERROR_MESSAGE_LOG_OPTIONS_WITHOUT_LOG_MATCHES,
    HELP_TEXT_ACL_RULE_LOG_OPTIONS,
)

__all__ = (
    "ACLAssignmentBulkEditForm",
    "ACLExtendedRuleBulkEditForm",
    "ACLStandardRuleBulkEditForm",
    "AccessListBulkEditForm",
)

ERROR_MESSAGE_CLEAR_LOG_OPTIONS_WITH_SELECTION = _("Clear log options cannot be combined with a log option selection.")


class AccessListBulkEditForm(PrimaryModelBulkEditForm):
    """
    Form for bulk editing multiple AccessList instances.
    """

    type = forms.ChoiceField(
        choices=add_blank_choice(ACLTypeChoices),
        required=False,
        label=_("Type"),
    )
    family = forms.ChoiceField(
        choices=add_blank_choice(ACLFamilyChoices),
        required=False,
        label=_("Family"),
    )
    default_action = forms.ChoiceField(
        choices=add_blank_choice(ACLActionChoices),
        required=False,
        label=_("Default Action"),
    )

    model = AccessList
    fieldsets = (
        FieldSet(
            "type",
            "family",
            "default_action",
            "description",
            name=_("Access List Details"),
        ),
    )
    nullable_fields = (
        "description",
        "comments",
    )


class ACLAssignmentBulkEditForm(GenericObjectFormMixin, OwnerMixin, NetBoxModelBulkEditForm):
    """
    Form for bulk editing multiple ACLStandardRule instances.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
        label=_("Access List"),
    )

    assigned_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_ASSIGNMENT_MODELS),
        required=False,
        selector=True,
        label=_("Assignment Object"),
        hx_method="post",
    )
    direction = forms.ChoiceField(
        choices=add_blank_choice(ACLAssignmentDirectionUIChoices),
        required=False,
        label=_("Direction"),
    )
    comments = CommentField()

    model = ACLAssignment
    fieldsets = (
        FieldSet(
            "access_list",
            name=_("Access List Details"),
        ),
        FieldSet(
            "assigned_object",
            "direction",
            name=_("Assignment"),
        ),
    )
    nullable_fields = ("comments",)

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACLAssignmentBulkEditForm.
        """
        super().__init__(*args, **kwargs)

        # Direction is declared enabled here, so with no type chosen a bulk edit can still change it alone.
        model = self.fields["assigned_object"].selected_model
        if model is not None and model not in (Interface, VMInterface):
            self.fields["direction"].disabled = True
            self.fields["direction"].widget.attrs["value"] = "None"


class ACLRuleLoggingBulkEditMixin(forms.Form):
    """
    Logging controls shared by both rule bulk edit forms.
    """

    log_matches = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("Log matches"),
        help_text=_("Setting this to No also removes every log option from the selected rules."),
    )
    log_options = forms.MultipleChoiceField(
        choices=ACLRuleLogOptionChoices,
        required=False,
        label=_("Log options"),
        help_text=HELP_TEXT_ACL_RULE_LOG_OPTIONS,
    )
    clear_log_options = forms.BooleanField(
        required=False,
        label=_("Clear log options"),
        help_text=_("Remove every log option while leaving Log matches as it is."),
    )

    def clean(self):
        """
        Apply the clear control, which exists because a blank selection means unchanged.
        """
        cleaned_data = super().clean()

        if cleaned_data.get("log_options"):
            if cleaned_data.get("clear_log_options"):
                raise forms.ValidationError(
                    {"clear_log_options": ERROR_MESSAGE_CLEAR_LOG_OPTIONS_WITH_SELECTION},
                )
            if cleaned_data.get("log_matches") is False:
                raise forms.ValidationError(
                    {"log_options": ERROR_MESSAGE_LOG_OPTIONS_WITHOUT_LOG_MATCHES},
                )

        if cleaned_data.get("log_matches") is False or cleaned_data.get("clear_log_options"):
            cleaned_data["log_options"] = []
            if "log_options" not in self.changed_data:
                self.changed_data.append("log_options")

        return cleaned_data


class ACLStandardRuleBulkEditForm(GenericObjectFormMixin, ACLRuleLoggingBulkEditMixin, PrimaryModelBulkEditForm):
    """
    Form for bulk editing multiple ACLStandardRule instances.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_STANDARD,
        },
        required=False,
        label=_("Access List"),
    )

    # Rule
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
        label=_("Action"),
    )

    # Remark
    remark = forms.CharField(
        max_length=500,
        required=False,
        label=_("Remark"),
    )

    # Source
    source = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Source"),
        hx_method="post",
    )

    model = ACLStandardRule
    fieldsets = (
        FieldSet(
            "access_list",
            "description",
            name=_("Access List Details"),
        ),
        FieldSet(
            "action",
            name=_("Rule Definition"),
        ),
        FieldSet(
            "remark",
            name=_("Remark"),
        ),
        FieldSet(
            "source",
            name=_("Source Definition"),
        ),
        FieldSet(
            "log_matches",
            "log_options",
            "clear_log_options",
            name=_("Logging"),
        ),
    )
    nullable_fields = (
        "remark",
        "source",
        "description",
        "comments",
    )


class ACLExtendedRuleBulkEditForm(GenericObjectFormMixin, ACLRuleLoggingBulkEditMixin, PrimaryModelBulkEditForm):
    """
    Form for bulk editing multiple ACLExtendedRule instances.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_EXTENDED,
        },
        required=False,
        label=_("Access List"),
    )

    # Rule
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
        label=_("Action"),
    )

    # Remark
    remark = forms.CharField(
        max_length=500,
        required=False,
        label=_("Remark"),
    )

    # Protocol
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ACLProtocolChoices),
        required=False,
        label=_("Protocol"),
    )

    # Source
    source = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Source"),
        hx_method="post",
    )
    source_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Source Port Ranges"),
    )

    # Destination
    destination = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Destination"),
        hx_method="post",
    )
    destination_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Destination Port Ranges"),
    )

    model = ACLExtendedRule
    fieldsets = (
        FieldSet(
            "access_list",
            "description",
            name=_("Access List Details"),
        ),
        FieldSet(
            "action",
            name=_("Rule Definition"),
        ),
        FieldSet(
            "remark",
            name=_("Remark"),
        ),
        FieldSet(
            "protocol",
            name=_("Protocol"),
        ),
        FieldSet(
            "source",
            "source_port_ranges",
            name=_("Source Definition"),
        ),
        FieldSet(
            "destination",
            "destination_port_ranges",
            name=_("Destination Definition"),
        ),
        FieldSet(
            "log_matches",
            "log_options",
            "clear_log_options",
            name=_("Logging"),
        ),
    )
    nullable_fields = (
        "remark",
        "source",
        "destination",
        "description",
        "comments",
    )
