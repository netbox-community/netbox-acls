"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, PrimaryModelForm
from netbox.forms.mixins import OwnerMixin
from utilities.forms import (
    add_blank_choice,
    get_field_value,
)
from utilities.forms.fields import (
    CommentField,
    ContentTypeChoiceField,
    DynamicModelChoiceField,
    NumericRangeArrayField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle
from virtualization.models import VMInterface

from ..choices import (
    ACLAssignmentDirectionChoices,
    ACLAssignmentDirectionUIChoices,
    ACLTypeChoices,
)
from ..constants import ACL_ASSIGNMENT_MODELS, ACL_RULE_SOURCE_DESTINATION_MODELS
from ..models import (
    AccessList,
    ACLAssignment,
    ACLExtendedRule,
    ACLStandardRule,
)

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


class ACLAssignmentForm(OwnerMixin, NetBoxModelForm):
    """
    GUI form to add or edit ACL assignments
    Requires an access_list, a name, a type, and a default_action.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        label="Access List",
        help_text=mark_safe(
            "<b>*Note:</b> Access List must be present on the device already.",
        ),
    )
    assigned_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_ASSIGNMENT_MODELS),
        widget=HTMXSelect(),
        label=_("Assignment Object Type"),
    )
    assigned_object = DynamicModelChoiceField(
        queryset=Device.objects.none(),  # Initial queryset
        selector=True,
        label=_("Assignment Object"),
        disabled=True,
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
            "assigned_object_type",
            "assigned_object",
            "direction",
            name=_("Assignment"),
        ),
    )

    class Meta:
        model = ACLAssignment
        fields = (
            "access_list",
            "assigned_object_type",
            "direction",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACL Assignment form.
        """

        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        initial["direction"] = ACLAssignmentDirectionChoices.DIRECTION_NONE

        if instance is not None and instance.assigned_object:
            # Initialize the assigned object field
            initial["assigned_object"] = instance.assigned_object
            initial["direction"] = instance.direction

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if assigned_object_type_id := get_field_value(self, "assigned_object_type"):
            try:
                # Retrieve the ContentType model class based on the assigned object type
                assigned_object_type = ContentType.objects.get(pk=assigned_object_type_id)
                assigned_object_model = assigned_object_type.model_class()

                # Configure the queryset and label for the assigned_object field
                self.fields["assigned_object"].queryset = assigned_object_model.objects.all()
                self.fields["assigned_object"].widget.attrs["selector"] = assigned_object_model._meta.label_lower
                self.fields["assigned_object"].disabled = False
                self.fields["assigned_object"].label = _(bettertitle(assigned_object_model._meta.verbose_name))
                if assigned_object_model in (Interface, VMInterface):
                    self.fields["direction"].disabled = False
                    self.fields["direction"].required = True
                    self.fields["direction"].choices = add_blank_choice(ACLAssignmentDirectionUIChoices)
                else:
                    self.fields["direction"].disabled = True
                    self.fields["direction"].widget.attrs["value"] = "None"
            except ObjectDoesNotExist:
                pass

            # Clears the assigned_object field if the selected type changes
            if self.instance and self.instance.pk and assigned_object_type_id != self.instance.assigned_object_type_id:
                self.initial["assigned_object"] = None

    def clean(self) -> None:
        """Validate form fields for the ACL Assignment form."""
        super().clean()

        # Ensure the selected object gets assigned
        self.instance.assigned_object = self.cleaned_data.get("assigned_object")


class ACLStandardRuleForm(PrimaryModelForm):
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
        help_text=mark_safe(
            _("<b>*Note:</b> This field will only display Standard ACLs."),
        ),
        label="Access List",
    )

    # Source
    source_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(),
        label=_("Source Type"),
        help_text=help_text_acl_rule_logic,
    )
    source = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Source"),
        help_text=help_text_acl_rule_logic,
        disabled=True,
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
            "source_type",
            "source",
            name=_("Source Definition"),
        ),
    )

    class Meta:
        model = ACLStandardRule
        fields = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "source_type",
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

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACLStandardRuleForm.
        """

        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.source:
            # Initialize the source object field
            initial["source"] = instance.source

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if source_type_id := get_field_value(self, "source_type"):
            try:
                # Retrieve the ContentType model class based on the source type
                source_type = ContentType.objects.get(pk=source_type_id)
                source_model = source_type.model_class()

                # Configure the queryset and label for the source field
                self.fields["source"].queryset = source_model.objects.all()
                self.fields["source"].widget.attrs["selector"] = source_model._meta.label_lower
                self.fields["source"].disabled = False
                self.fields["source"].label = _("Source " + bettertitle(source_model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            # Clears the source field if the selected type changes
            if self.instance and self.instance.pk and source_type_id != self.instance.source_type_id:
                self.initial["source"] = None

    def clean(self):
        """
        Validate form fields for the ACL Standard Rule form.
        """
        super().clean()

        # Ensure the selected source object gets assigned
        self.instance.source = self.cleaned_data.get("source")


class ACLExtendedRuleForm(PrimaryModelForm):
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
        help_text=mark_safe(
            _("<b>*Note:</b> This field will only display Extended ACLs."),
        ),
        label="Access List",
    )

    # Source
    source_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(),
        label=_("Source Type"),
        help_text=help_text_acl_rule_logic,
    )
    source = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Source"),
        help_text=help_text_acl_rule_logic,
        disabled=True,
    )
    source_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Source Port Ranges"),
        help_text=(help_text_acl_rule_port_logic + " " + help_text_acl_rule_port_ranges),
    )

    # Destination
    destination_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(),
        label=_("Destination Type"),
        help_text=help_text_acl_rule_logic,
    )
    destination = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Destination"),
        help_text=help_text_acl_rule_logic,
        disabled=True,
    )
    destination_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Destination Port Ranges"),
        help_text=(help_text_acl_rule_port_logic + " " + help_text_acl_rule_port_ranges),
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
            "source_type",
            "source",
            "source_port_ranges",
            name=_("Source Definition"),
        ),
        FieldSet(
            "destination_type",
            "destination",
            "destination_port_ranges",
            name=_("Destination Definition"),
        ),
    )

    class Meta:
        model = ACLExtendedRule
        fields = (
            "access_list",
            "sequence",
            "action",
            "remark",
            "source_type",
            "source_port_ranges",
            "destination_type",
            "destination_port_ranges",
            "protocol",
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

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACLExtendedRuleForm.
        """

        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.source:
            # Initialize the source object field
            initial["source"] = instance.source
        if instance is not None and instance.destination:
            # Initialize the destination object field
            initial["destination"] = instance.destination

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        # Source
        if source_type_id := get_field_value(self, "source_type"):
            try:
                # Retrieve the ContentType model class based on the source type
                source_type = ContentType.objects.get(pk=source_type_id)
                source_model = source_type.model_class()

                # Configure the queryset and label for the source field
                self.fields["source"].queryset = source_model.objects.all()
                self.fields["source"].widget.attrs["selector"] = source_model._meta.label_lower
                self.fields["source"].disabled = False
                self.fields["source"].label = _("Source " + bettertitle(source_model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            # Clears the source field if the selected type changes
            if self.instance and self.instance.pk and source_type_id != self.instance.source_type_id:
                self.initial["source"] = None

        # Destination
        if destination_type_id := get_field_value(self, "destination_type"):
            try:
                # Retrieve the ContentType model class based on the destination type
                destination_type = ContentType.objects.get(pk=destination_type_id)
                destination_model = destination_type.model_class()

                # Configure the queryset and label for the destination field
                self.fields["destination"].queryset = destination_model.objects.all()
                self.fields["destination"].widget.attrs["selector"] = destination_model._meta.label_lower
                self.fields["destination"].disabled = False
                self.fields["destination"].label = _("Destination " + bettertitle(destination_model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            # Clears the destination field if the selected type changes
            if self.instance and self.instance.pk and destination_type_id != self.instance.destination_type_id:
                self.initial["destination"] = None

    def clean(self):
        """
        Validate form fields for the ACL Extended Rule form.
        """
        super().clean()

        # Ensure the selected source object gets assigned
        self.instance.source = self.cleaned_data.get("source")

        # Ensure the selected destination object gets assigned
        self.instance.destination = self.cleaned_data.get("destination")
