"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelForm, PrimaryModelForm
from netbox.forms.mixins import OwnerMixin
from utilities.forms.fields import (
    ChoiceField,
    CommentField,
    DynamicModelChoiceField,
    GenericObjectChoiceField,
    MultipleChoiceField,
    NumericRangeArrayField,
)
from utilities.forms.mixins import GenericObjectFormMixin
from utilities.forms.rendering import FieldSet
from utilities.forms.utils import add_blank_choice
from utilities.forms.widgets import HTMXSelect, NumberWithOptions

from ..choices import (
    ACLActionChoices,
    ACLAddressFamilyChoices,
    ACLAssignmentInterfaceDirectionChoices,
    ACLFamilyChoices,
    ACLICMPTypeChoices,
    ACLICMPv4TypeChoices,
    ACLICMPv6TypeChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTCPFlagChoices,
    ACLTCPFlagMatchChoices,
    ACLTypeChoices,
)
from ..constants import ACL_ADDRESS_OBJECT_MODELS, ACL_ASSIGNMENT_MODELS, ACL_RULE_SOURCE_DESTINATION_MODELS
from ..models import (
    AccessList,
    ACLAddressGroup,
    ACLAddressGroupMember,
    ACLAssignment,
    ACLExtendedRule,
    ACLStandardRule,
)

__all__ = (
    "ACLAddressGroupForm",
    "ACLAddressGroupMemberForm",
    "ACLAssignmentForm",
    "ACLExtendedRuleForm",
    "ACLStandardRuleForm",
    "AccessListForm",
)


#
# Access Lists
#


class AccessListForm(PrimaryModelForm):
    """
    GUI form to add or edit an AccessList.
    Requires a device, a name, a type, and a default_action.
    """

    type = ChoiceField(
        choices=add_blank_choice(ACLTypeChoices),
        label=_("Type"),
        help_text=_("Cannot change while the access list has rules."),
    )
    family = ChoiceField(
        choices=ACLFamilyChoices,
        initial=ACLFamilyChoices.FAMILY_IPV4,
        label=_("Family"),
        help_text=_("Cannot change while the access list has rules."),
    )
    default_action = ChoiceField(
        choices=ACLActionChoices,
        initial=ACLActionChoices.ACTION_DENY,
        label=_("Default Action"),
        help_text=_("Applies to traffic that matches no rule."),
    )

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
            "name": _("The name uniqueness per device is case insensitive."),
        }


#
# Assignments
#


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
    direction = ChoiceField(
        choices=add_blank_choice(ACLAssignmentInterfaceDirectionChoices),
        label=_("Direction"),
        help_text=_(
            "Only one ACL per address family can be assigned to the same interface and direction, "
            "and a Dual ACL counts as both."
        ),
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
        super().__init__(*args, **kwargs)

        if self.fields["assigned_object"].selected_model not in ACLAssignment.interface_models:
            del self.fields["direction"]

    def clean(self):
        """
        Point the instance at the posted object, or at none, so model validation never checks a stale one.
        """
        # Model validation still runs when super().clean() raises
        self.instance.assigned_object = self.cleaned_data.get("assigned_object")

        return super().clean()


#
# Rules
#


class ACLRuleFormMixin:
    """
    Show only the rule fields that apply to the selected action and protocol.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Hide the fields and fieldsets that do not apply.
        """
        super().__init__(*args, **kwargs)

        self._hidden_fields = self._get_hidden_fields()
        for field_name in self._hidden_fields:
            del self.fields[field_name]

        # An emptied fieldset would still render its heading
        self.fieldsets = tuple(
            fieldset for fieldset in self.fieldsets if any(item in self.fields for item in fieldset.items)
        )

    def clean(self):
        """
        Clear the hidden fields on the instance, since add_error rejects a model error on a deleted one.
        """
        # Model validation still runs when super().clean() raises
        for field_name in self._hidden_fields:
            field = self.instance._meta.get_field(field_name)
            setattr(self.instance, field_name, None if isinstance(field, GenericForeignKey) else field.get_default())

        return super().clean()

    def _get_hidden_fields(self) -> set[str]:
        """
        Return the fields that do not apply to the selected action.
        """
        action = self["action"].value()
        if not action or action == ACLRuleActionChoices.ACTION_REMARK:
            return {"source", "log_matches", "log_options"}
        return set()


class ACLStandardRuleForm(ACLRuleFormMixin, GenericObjectFormMixin, PrimaryModelForm):
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

    # Rule
    action = ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        widget=HTMXSelect(),
        label=_("Action"),
    )

    # Source
    source = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Source"),
        help_text=_("Leave empty to match any source."),
        hx_target_id="source-definition",
    )

    log_options = MultipleChoiceField(
        choices=ACLRuleLogOptionChoices,
        required=False,
        label=_("Log options"),
        help_text=_(
            "Optional logging attributes. Leave empty for the target platform's default. "
            "Vendor-specific options are grouped by vendor and are platform-dependent."
        ),
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


class ACLExtendedRuleForm(ACLRuleFormMixin, GenericObjectFormMixin, PrimaryModelForm):
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

    # Rule
    action = ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        widget=HTMXSelect(),
        label=_("Action"),
    )

    # Protocol
    protocol = ChoiceField(
        choices=add_blank_choice(ACLProtocolChoices),
        required=False,
        widget=HTMXSelect(),
        label=_("Protocol"),
    )

    # Source
    source = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Source"),
        help_text=_("Leave empty to match any source."),
        hx_target_id="source-definition",
    )
    source_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Source Port Ranges"),
        help_text=_(
            "Comma-separated port numbers. An inclusive range may be specified using a hyphen "
            "(e.g. 22,80-81,1024-65535). Leave empty to match any port."
        ),
    )

    # Destination
    destination = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        selector=True,
        label=_("Destination"),
        help_text=_("Leave empty to match any destination."),
        hx_target_id="destination-definition",
    )
    destination_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Destination Port Ranges"),
        help_text=_(
            "Comma-separated port numbers. An inclusive range may be specified using a hyphen "
            "(e.g. 22,80-81,1024-65535). Leave empty to match any port."
        ),
    )

    # TCP flags
    tcp_flags = MultipleChoiceField(
        choices=ACLTCPFlagChoices,
        required=False,
        label=_("TCP Flags"),
        help_text=_("Unselected flags are ignored. ACK and RST with Any is the stateless established match."),
    )
    tcp_flags_match = ChoiceField(
        choices=ACLTCPFlagMatchChoices,
        initial=ACLTCPFlagMatchChoices.MATCH_ALL,
        label=_("TCP Flags Match"),
        help_text=_("Ignored when no flags are selected."),
    )

    log_options = MultipleChoiceField(
        choices=ACLRuleLogOptionChoices,
        required=False,
        label=_("Log options"),
        help_text=_(
            "Optional logging attributes. Leave empty for the target platform's default. "
            "Vendor-specific options are grouped by vendor and are platform-dependent."
        ),
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
            "icmp_type",
            "icmp_code",
            name=_("ICMP"),
        ),
        FieldSet(
            "tcp_flags",
            "tcp_flags_match",
            name=_("TCP Flags"),
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
            "icmp_type",
            "icmp_code",
            "tcp_flags",
            "tcp_flags_match",
            "log_matches",
            "log_options",
            "description",
            "owner",
            "comments",
            "tags",
        )

        widgets = {
            "icmp_type": NumberWithOptions(options=ACLICMPTypeChoices),
        }

    def __init__(self, *args, **kwargs) -> None:
        """
        Offer the ICMP type presets of the selected protocol's family.
        """
        super().__init__(*args, **kwargs)

        if "icmp_type" in self.fields:
            protocol = self["protocol"].value()
            if protocol == ACLProtocolChoices.PROTOCOL_ICMPV4:
                self.fields["icmp_type"].widget.options = ACLICMPv4TypeChoices
            elif protocol == ACLProtocolChoices.PROTOCOL_ICMPV6:
                self.fields["icmp_type"].widget.options = ACLICMPv6TypeChoices

    def _get_hidden_fields(self) -> set[str]:
        """
        Return the fields that do not apply to the selected action or protocol.
        """
        hidden_fields = super()._get_hidden_fields()
        action = self["action"].value()
        if not action or action == ACLRuleActionChoices.ACTION_REMARK:
            hidden_fields |= {
                "destination",
                "protocol",
                "source_port_ranges",
                "destination_port_ranges",
                "icmp_type",
                "icmp_code",
                "tcp_flags",
                "tcp_flags_match",
            }
        else:
            protocol = self["protocol"].value()
            if protocol not in [
                ACLProtocolChoices.PROTOCOL_TCP,
                ACLProtocolChoices.PROTOCOL_UDP,
            ]:
                hidden_fields |= {"source_port_ranges", "destination_port_ranges"}
            if protocol not in [
                ACLProtocolChoices.PROTOCOL_ICMP,
                ACLProtocolChoices.PROTOCOL_ICMPV4,
                ACLProtocolChoices.PROTOCOL_ICMPV6,
            ]:
                hidden_fields |= {"icmp_type", "icmp_code"}
            if protocol != ACLProtocolChoices.PROTOCOL_TCP:
                hidden_fields |= {"tcp_flags", "tcp_flags_match"}
        return hidden_fields


#
# Address Groups
#


class ACLAddressGroupForm(PrimaryModelForm):
    """
    GUI form to add or edit an ACLAddressGroup.
    """

    family = ChoiceField(
        choices=ACLAddressFamilyChoices,
        initial=ACLAddressFamilyChoices.FAMILY_IPV4,
        label=_("Family"),
        help_text=_("Cannot change while the group has members or is referenced by rules."),
    )

    fieldsets = (
        FieldSet(
            "name",
            "family",
            "description",
            "tags",
            name=_("Address Group Details"),
        ),
    )

    class Meta:
        model = ACLAddressGroup
        fields = (
            "name",
            "family",
            "description",
            "owner",
            "comments",
            "tags",
        )

        help_texts = {
            "name": _("Globally unique name. Letters, numbers, underscores and hyphens only."),
        }


class ACLAddressGroupMemberForm(GenericObjectFormMixin, OwnerMixin, NetBoxModelForm):
    """
    GUI form to add or edit an ACLAddressGroupMember.
    """

    address_group = DynamicModelChoiceField(
        queryset=ACLAddressGroup.objects.all(),
        label=_("Address Group"),
    )
    member = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ACL_ADDRESS_OBJECT_MODELS),
        selector=True,
        label=_("Member"),
        help_text=_("The member must have the same IP family as the address group."),
        hx_target_id="member-definition",
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "address_group",
            "tags",
            name=_("Address Group Details"),
        ),
        FieldSet(
            "member",
            name=_("Member"),
            html_id="member-definition",
        ),
    )

    class Meta:
        model = ACLAddressGroupMember
        fields = (
            "address_group",
            "owner",
            "comments",
            "tags",
        )
