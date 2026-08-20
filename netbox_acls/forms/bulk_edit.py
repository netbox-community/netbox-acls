"""
Defines each django model's GUI form to edit multiple objects at once.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface
from ipam.models import Prefix
from netbox.forms import NetBoxModelBulkEditForm, PrimaryModelBulkEditForm
from netbox.forms.mixins import OwnerMixin
from utilities.forms.fields import CommentField, ContentTypeChoiceField, DynamicModelChoiceField, NumericRangeArrayField
from utilities.forms.rendering import FieldSet
from utilities.forms.utils import add_blank_choice, get_field_value
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle
from virtualization.models import VMInterface

from ..choices import (
    ACLActionChoices,
    ACLAssignmentDirectionUIChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ..constants import ACL_ASSIGNMENT_MODELS, ACL_RULE_SOURCE_DESTINATION_MODELS
from ..models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule

__all__ = (
    "ACLAssignmentBulkEditForm",
    "ACLExtendedRuleBulkEditForm",
    "ACLStandardRuleBulkEditForm",
    "AccessListBulkEditForm",
)


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


class ACLAssignmentBulkEditForm(OwnerMixin, NetBoxModelBulkEditForm):
    """
    Form for bulk editing multiple ACLStandardRule instances.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
        label=_("Access List"),
    )

    assigned_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_ASSIGNMENT_MODELS),
        required=False,
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        label=_("Assignment Type"),
    )
    assigned_object = DynamicModelChoiceField(
        queryset=Device.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Assignment Object"),
        disabled=True,
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
            "assigned_object_type",
            "assigned_object",
            "direction",
            name=_("Assignment"),
        ),
    )
    nullable_fields = ("comments",)

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACLStandardRuleForm.
        """
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
                    self.fields["direction"].choices = add_blank_choice(ACLAssignmentDirectionUIChoices)
                else:
                    self.fields["direction"].disabled = True
                    self.fields["direction"].widget.attrs["value"] = "None"
            except ObjectDoesNotExist:
                pass


class ACLStandardRuleBulkEditForm(PrimaryModelBulkEditForm):
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
    source_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        label=_("Source Type"),
    )
    source = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Source"),
        disabled=True,
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
            "source_type",
            "source",
            name=_("Source Definition"),
        ),
    )
    nullable_fields = (
        "remark",
        "source_type",
        "source",
        "description",
        "comments",
    )

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACLStandardRuleForm.
        """
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


class ACLExtendedRuleBulkEditForm(PrimaryModelBulkEditForm):
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
    source_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        label=_("Source Type"),
    )
    source = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Source"),
        disabled=True,
    )
    source_port_ranges = NumericRangeArrayField(
        required=False,
        label=_("Source Port Ranges"),
    )

    # Destination
    destination_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        label=_("Destination Type"),
    )
    destination = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Destination"),
        disabled=True,
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
    nullable_fields = (
        "remark",
        "source_type",
        "source",
        "destination_type",
        "destination",
        "description",
        "comments",
    )

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACLExtendedRuleForm.
        """
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
