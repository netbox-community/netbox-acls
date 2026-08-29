"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from dcim.models import Interface
from netbox.forms import NetBoxModelForm, PrimaryModelForm
from netbox.forms.mixins import OwnerMixin
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    GenericObjectChoiceField,
    NumericRangeArrayField,
)
from utilities.forms.mixins import GenericObjectFormMixin
from utilities.forms.rendering import FieldSet
from virtualization.models import VMInterface

from ..choices import (
    ACLAssignmentDirectionChoices,
    ACLAssignmentDirectionUIChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ..constants import ACL_ASSIGNMENT_MODELS, ACL_RULE_SOURCE_DESTINATION_MODELS
from ..models import (
    AccessList,
    ACLAssignment,
    ACLExtendedRule,
    ACLStandardRule,
)
from ..models.access_list_rules import HELP_TEXT_ACL_RULE_LOG_OPTIONS

__all__ = (
    "ACLAssignmentForm",
    "ACLExtendedRuleForm",
    "ACLStandardRuleForm",
    "AccessListForm",
)

# Sets a standard mark_safe help_text value to be used by the various classes
help_text_acl_rule_logic = mark_safe(
    _("<b>*Note:</b> CANNOT be set if action is set to remark."),
)
# Sets a standard mark_safe help_text value to be used by the various classes
help_text_acl_rule_port_logic = mark_safe(
    _("<b>*Note:</b> CANNOT be set if action is set to remark. Only valid when protocol is TCP or UDP.")
)
# Sets a standard help_text value to be used by the various classes for acl action
help_text_acl_action = _("Action the rule will take (remark, deny, or allow).")
# Sets a standard help_text value to be used by the various classes for acl sequence
help_text_acl_rule_sequence = _("Determines the order of the rule in the ACL processing.")
# Standard help_text value to be used by the various classes for acl remark
help_text_acl_remark = _("Remark the rule will take.")
# Sets a standard help_text value to be used by the fields for acl port ranges
help_text_acl_rule_port_ranges = _("Comma/hyphen (inclusive). Example: 22,80-81,1024-65535")


class AccessListForm(PrimaryModelForm):
    """
    GUI form to add or edit an AccessList.
    Requires a device, a name, a type, and a default_action.
    """

    fieldsets = (
        FieldSet(
            "name",
            "type",
            "family",
            "default_action",
            "description",
            "tags",
            name=_("Access List Details"),
        ),
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
            "default_action": _("The default behavior of the ACL."),
            "family": _(
                "Determines whether this ACL contains IPv4, IPv6, or dual-stack rules."
                "Cannot be changed if rules are associated."
            ),
            "name": _("The name uniqueness per device is case insensitive."),
            "type": mark_safe(
                _("<b>*Note:</b> CANNOT be changed if ACL Rules are associated to this Access List."),
            ),
        }


class ACLAssignmentForm(GenericObjectFormMixin, OwnerMixin, NetBoxModelForm):
    """
    GUI form to add or edit ACL assignments
    Requires an access_list, a name, a type, and a default_action.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        label=_("Access List"),
        help_text=mark_safe(
            "<b>*Note:</b> Access List must be present on the device already.",
        ),
    )
    assigned_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_ASSIGNMENT_MODELS),
        selector=True,
        label=_("Assignment Object"),
        hx_target_id="acl-assignment",
    )
    direction = forms.ChoiceField(
        choices=add_blank_choice(ACLAssignmentDirectionChoices),
        required=False,
        label=_("Direction"),
        help_text=_(
            "The ACL assignment direction field is only enabled for "
            "Device Interface or Virtual Machine Interface objects. "
            "For other types (such as Device, Virtual Chassis, or Virtual Machine), "
            "this field is disabled. "
            "<b>*Note:</b> CANNOT assign 2 ACLs to the same interface & direction.",
        ),
        disabled=True,
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "access_list",
            "tags",
            name=_("Access List Details"),
        ),
        FieldSet(
            "assigned_object",
            "direction",
            name=_("Assignment"),
            html_id="acl-assignment",
        ),
    )

    class Meta:
        model = ACLAssignment
        fields = (
            "access_list",
            "direction",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACL Assignment form.
        """
        # The add view passes an unsaved instance rather than None, so test the pk.
        # BaseModelForm applies initial over model_to_dict(instance), so seeding
        # unconditionally would reset a stored direction.
        if (instance := kwargs.get("instance")) is None or instance.pk is None:
            initial = kwargs.get("initial", {}).copy()
            initial.setdefault("direction", ACLAssignmentDirectionChoices.DIRECTION_NONE)
            kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        # With no type chosen the field keeps its declared disabled state.
        if (model := self.fields["assigned_object"].selected_model) is not None:
            if model in (Interface, VMInterface):
                self.fields["direction"].disabled = False
                self.fields["direction"].required = True
                self.fields["direction"].choices = add_blank_choice(ACLAssignmentDirectionUIChoices)
            else:
                self.fields["direction"].disabled = True
                self.fields["direction"].widget.attrs["value"] = "None"


class ACLStandardRuleForm(GenericObjectFormMixin, PrimaryModelForm):
    """
    GUI form to add or edit Standard Access List.
    Requires an access_list, a sequence, and ACL rule type.
    See the clean function for logic on other field requirements.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_STANDARD,
        },
        label=_("Access List"),
        help_text=mark_safe(
            _("<b>*Note:</b> This field will only display Standard ACLs."),
        ),
    )

    # Source
    source = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Source"),
        help_text=help_text_acl_rule_logic,
        hx_target_id="source-definition",
    )

    log_options = forms.MultipleChoiceField(
        choices=ACLRuleLogOptionChoices,
        required=False,
        label=_("Log options"),
        help_text=HELP_TEXT_ACL_RULE_LOG_OPTIONS,
    )

    fieldsets = (
        FieldSet(
            "access_list",
            "description",
            "tags",
            name=_("Access List Details"),
        ),
        FieldSet(
            "sequence",
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
            html_id="source-definition",
        ),
        FieldSet(
            "log_matches",
            "log_options",
            name=_("Logging"),
        ),
    )

    class Meta:
        model = ACLStandardRule
        fields = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "log_matches",
            "log_options",
            "description",
            "owner",
            "comments",
            "tags",
        )

        help_texts = {
            "sequence": help_text_acl_rule_sequence,
            "action": help_text_acl_action,
            "remark": help_text_acl_remark,
        }


class ACLExtendedRuleForm(GenericObjectFormMixin, PrimaryModelForm):
    """
    GUI form to add or edit Extended Access List.
    Requires an access_list, a sequence, and ACL rule type.
    See the clean function for logic on other field requirements.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_EXTENDED,
        },
        label=_("Access List"),
        help_text=mark_safe(
            _("<b>*Note:</b> This field will only display Extended ACLs."),
        ),
    )

    # Source
    source = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Source"),
        help_text=help_text_acl_rule_logic,
        hx_target_id="source-definition",
    )
    source_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Source Port Ranges"),
        help_text=(help_text_acl_rule_port_logic + " " + help_text_acl_rule_port_ranges),
    )

    # Destination
    destination = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Destination"),
        help_text=help_text_acl_rule_logic,
        hx_target_id="destination-definition",
    )
    destination_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Destination Port Ranges"),
        help_text=(help_text_acl_rule_port_logic + " " + help_text_acl_rule_port_ranges),
    )

    log_options = forms.MultipleChoiceField(
        choices=ACLRuleLogOptionChoices,
        required=False,
        label=_("Log options"),
        help_text=HELP_TEXT_ACL_RULE_LOG_OPTIONS,
    )

    fieldsets = (
        FieldSet(
            "access_list",
            "description",
            "tags",
            name=_("Access List Details"),
        ),
        FieldSet(
            "sequence",
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
            html_id="source-definition",
        ),
        FieldSet(
            "destination",
            "destination_port_ranges",
            name=_("Destination Definition"),
            html_id="destination-definition",
        ),
        FieldSet(
            "log_matches",
            "log_options",
            name=_("Logging"),
        ),
    )

    class Meta:
        model = ACLExtendedRule
        fields = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "source_port_ranges",
            "destination_port_ranges",
            "protocol",
            "log_matches",
            "log_options",
            "description",
            "owner",
            "comments",
            "tags",
        )

        help_texts = {
            "action": help_text_acl_action,
            "sequence": help_text_acl_rule_sequence,
            "protocol": help_text_acl_rule_logic,
            "remark": help_text_acl_remark,
        }
