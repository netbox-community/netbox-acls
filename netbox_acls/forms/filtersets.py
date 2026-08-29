"""
Defines each django model's GUI filter/search options.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.forms import NetBoxModelFilterSetForm, PrimaryModelFilterSetForm
from netbox.forms.mixins import OwnerFilterMixin
from utilities.forms.constants import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import (
    ContentTypeMultipleChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from virtualization.models import VirtualMachine, VMInterface

from ..choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ..constants import ACL_ASSIGNMENT_MODELS
from ..models import (
    AccessList,
    ACLAssignment,
    ACLExtendedRule,
    ACLStandardRule,
)

__all__ = (
    "ACLAssignmentFilterForm",
    "ACLExtendedRuleFilterForm",
    "ACLStandardRuleFilterForm",
    "AccessListFilterForm",
)


class AccessListFilterForm(PrimaryModelFilterSetForm):
    """
    GUI filter form to search the django AccessList model.
    """

    model = AccessList
    fieldsets = (
        FieldSet(
            "q",
            "tag",
            name=None,
        ),
        FieldSet(
            "type",
            "family",
            "default_action",
            "description",
            name=_("ACL Details"),
        ),
        FieldSet(
            "owner_group_id",
            "owner_id",
            name=_("Ownership"),
        ),
    )

    # ACL selector
    type = forms.MultipleChoiceField(
        choices=ACLTypeChoices,
        required=False,
        label=_("Type"),
    )
    family = forms.MultipleChoiceField(
        choices=ACLFamilyChoices,
        required=False,
        label=_("Family"),
    )
    default_action = forms.MultipleChoiceField(
        choices=ACLActionChoices,
        required=False,
        label=_("Default Action"),
    )

    # Tag selector
    tag = TagFilterField(model)


class ACLAssignmentFilterForm(OwnerFilterMixin, NetBoxModelFilterSetForm):
    """
    GUI filter form to search the django ACLAssignment model.
    """

    model = ACLAssignment
    fieldsets = (
        FieldSet(
            "q",
            "tag",
            name=None,
        ),
        FieldSet(
            "access_list_id",
            "assigned_object_type_id",
            "family",
            "direction",
            name=_("ACL Details"),
        ),
        FieldSet(
            "region_id",
            "site_group_id",
            "site_id",
            "device_id",
            "interface_id",
            name=_("Device Details"),
        ),
        FieldSet(
            "virtual_chassis_id",
            name=_("Virtual Chassis Details"),
        ),
        FieldSet(
            "virtual_machine_id",
            "vminterface_id",
            name=_("Virtual Machine Details"),
        ),
        FieldSet(
            "owner_group_id",
            "owner_id",
            name=_("Ownership"),
        ),
    )

    # ACL selector
    access_list_id = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
        label=_("Access List"),
    )
    assigned_object_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(ACL_ASSIGNMENT_MODELS),
        required=False,
        label=_("Assigned Object Type"),
    )
    family = forms.MultipleChoiceField(
        choices=ACLFamilyChoices,
        required=False,
        label=_("Family"),
    )
    direction = forms.MultipleChoiceField(
        choices=ACLAssignmentDirectionChoices,
        required=False,
        label=_("Direction"),
    )

    # Device and Interface selectors
    region_id = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_("Region"),
    )
    site_group_id = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_("Site Group"),
    )
    site_id = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            "region_id": "$region_id",
            "group_id": "$site_group_id",
        },
        label=_("Site"),
    )
    device_id = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            "region_id": "$region_id",
            "group_id": "$site_group_id",
            "site_id": "$site_id",
        },
        required=False,
        label=_("Device"),
    )
    interface_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            "device_id": "$device_id",
        },
        label=_("Device Interface"),
    )

    # Virtual Chassis selector
    virtual_chassis_id = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label=_("Virtual Chassis"),
    )

    # Virtual Machine and VM Interface selectors
    virtual_machine_id = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_("Virtual Machine"),
    )
    vminterface_id = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        query_params={
            "virtual_machine_id": "$virtual_machine_id",
        },
        label=_("VM Interface"),
    )

    # Tag selector
    tag = TagFilterField(model)


class ACLRuleFilterFormMixin(forms.Form):
    """
    Filter fields shared by both concrete rule filter forms.

    The Access List picker stays on each concrete form, since the two narrow it
    to different ACL types.
    """

    sequence = forms.IntegerField(
        required=False,
        label=_("Sequence"),
    )
    action = forms.MultipleChoiceField(
        choices=ACLRuleActionChoices,
        required=False,
        label=_("Action"),
    )
    remark = forms.CharField(
        required=False,
        label=_("Remark"),
    )

    # Logging
    log_matches = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Log matches"),
    )
    log_options = forms.MultipleChoiceField(
        choices=ACLRuleLogOptionChoices,
        required=False,
        label=_("Log options"),
    )

    # Source selectors
    source_aggregate_id = DynamicModelMultipleChoiceField(
        queryset=Aggregate.objects.all(),
        required=False,
        label=_("Source Aggregate"),
    )
    source_ipaddress_id = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label=_("Source IP-Address"),
    )
    source_iprange_id = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label=_("Source IP-Range"),
    )
    source_prefix_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("Source Prefix"),
    )


class ACLStandardRuleFilterForm(ACLRuleFilterFormMixin, PrimaryModelFilterSetForm):
    """
    GUI filter form to search the django ACLStandardRule model.
    """

    model = ACLStandardRule
    fieldsets = (
        FieldSet(
            "q",
            "tag",
            name=None,
        ),
        FieldSet(
            "access_list_id",
            "sequence",
            "action",
            "remark",
            name=_("ACL Details"),
        ),
        FieldSet(
            "source_aggregate_id",
            "source_ipaddress_id",
            "source_iprange_id",
            "source_prefix_id",
            name=_("Source Details"),
        ),
        FieldSet(
            "log_matches",
            "log_options",
            name=_("Logging"),
        ),
        FieldSet(
            "owner_group_id",
            "owner_id",
            name=_("Ownership"),
        ),
    )

    access_list_id = DynamicModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_STANDARD,
        },
        required=False,
        label=_("Access List"),
    )

    # Tag selector
    tag = TagFilterField(model)


class ACLExtendedRuleFilterForm(ACLRuleFilterFormMixin, PrimaryModelFilterSetForm):
    """
    GUI filter form to search the django ACLExtendedRule model.
    """

    model = ACLExtendedRule
    fieldsets = (
        FieldSet(
            "q",
            "tag",
            name=None,
        ),
        FieldSet(
            "access_list_id",
            "sequence",
            "action",
            "remark",
            "protocol",
            name=_("ACL Details"),
        ),
        FieldSet(
            "source_aggregate_id",
            "source_ipaddress_id",
            "source_iprange_id",
            "source_prefix_id",
            "source_port",
            name=_("Source Details"),
        ),
        FieldSet(
            "destination_aggregate_id",
            "destination_ipaddress_id",
            "destination_iprange_id",
            "destination_prefix_id",
            "destination_port",
            name=_("Destination Details"),
        ),
        FieldSet(
            "log_matches",
            "log_options",
            name=_("Logging"),
        ),
        FieldSet(
            "owner_group_id",
            "owner_id",
            name=_("Ownership"),
        ),
    )

    access_list_id = DynamicModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_EXTENDED,
        },
        required=False,
        label=_("Access List"),
    )
    protocol = forms.MultipleChoiceField(
        choices=ACLProtocolChoices,
        required=False,
        label=_("Protocol"),
    )

    source_port = forms.IntegerField(
        label=_("Source Port"),
        required=False,
    )

    # Destination selectors
    destination_aggregate_id = DynamicModelMultipleChoiceField(
        queryset=Aggregate.objects.all(),
        required=False,
        label=_("Destination Aggregate"),
    )
    destination_ipaddress_id = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label=_("Destination IP-Address"),
    )
    destination_iprange_id = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label=_("Destination IP-Range"),
    )
    destination_prefix_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("Destination Prefix"),
    )
    destination_port = forms.IntegerField(
        label=_("Destination Port"),
        required=False,
    )

    # Tag selector
    tag = TagFilterField(model)
