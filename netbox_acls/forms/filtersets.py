"""
Defines each django model's GUI filter/search options.
"""

from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from django import forms
from django.utils.translation import gettext_lazy as _
from ipam.models import Prefix
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.utils import add_blank_choice
from virtualization.models import VirtualMachine, VMInterface

from ..choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ..models import (
    AccessList,
    ACLExtendedRule,
    ACLInterfaceAssignment,
    ACLStandardRule,
)

__all__ = (
    "AccessListFilterForm",
    "ACLInterfaceAssignmentFilterForm",
    "ACLStandardRuleFilterForm",
    "ACLExtendedRuleFilterForm",
)


class AccessListFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter form to search the django AccessList model.
    """

    model = AccessList
    fieldsets = (
        FieldSet("q", "tag", name=None),
        FieldSet("type", "default_action", name=_("ACL Details")),
        FieldSet("region_id", "site_group_id", "site_id", "device_id", name=_("Device Details")),
        FieldSet("virtual_chassis_id", name=_("Virtual Chassis Details")),
        FieldSet("virtual_machine_id", name=_("Virtual Machine Details")),
    )

    # ACL
    type = forms.ChoiceField(
        choices=add_blank_choice(ACLTypeChoices),
        required=False,
    )
    default_action = forms.ChoiceField(
        choices=add_blank_choice(ACLActionChoices),
        required=False,
        label=_("Default Action"),
    )

    # Device selector
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

    # Virtual Chassis selector
    virtual_chassis_id = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label=_("Virtual Chassis"),
    )

    # Virtual Machine selector
    virtual_machine_id = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_("Virtual Machine"),
    )

    # Tag selector
    tag = TagFilterField(model)


class ACLInterfaceAssignmentFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter form to search the django AccessList model.
    """

    model = ACLInterfaceAssignment
    fieldsets = (
        FieldSet("q", "tag", name=None),
        FieldSet("access_list_id", "direction", name=_("ACL Details")),
        FieldSet("region_id", "site_group_id", "site_id", "device_id", "interface_id", name=_("Device Details")),
        FieldSet("virtual_machine_id", "vminterface_id", name=_("Virtual Machine Details")),
    )

    # ACL selector
    access_list_id = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
        label=_("Access List"),
    )
    direction = forms.ChoiceField(
        choices=add_blank_choice(ACLAssignmentDirectionChoices),
        required=False,
        label=_("Direction"),
    )

    # Device Interface selector
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

    # Virtual Machine Interface selector
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


class ACLStandardRuleFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter form to search the django ACLStandardRule model.
    """

    model = ACLStandardRule
    fieldsets = (
        FieldSet("q", "tag", name=None),
        FieldSet("access_list_id", "index", "action", name=_("ACL Details")),
        FieldSet("source_prefix_id", name=_("Source Details")),
    )

    access_list_id = DynamicModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_STANDARD,
        },
        required=False,
        label=_("Access List"),
    )
    index = forms.IntegerField(
        required=False,
        label=_("Index"),
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
        label=_("Action"),
    )

    # Source selectors
    source_prefix_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("Source Prefix"),
    )

    # Tag selector
    tag = TagFilterField(model)


class ACLExtendedRuleFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter form to search the django ACLExtendedRule model.
    """

    model = ACLExtendedRule
    fieldsets = (
        FieldSet("q", "tag", name=None),
        FieldSet("access_list_id", "index", "action", "protocol", name=_("ACL Details")),
        FieldSet("source_prefix_id", name=_("Source Details")),
        FieldSet("destination_prefix_id", name=_("Destination Details")),
    )

    access_list_id = DynamicModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_EXTENDED,
        },
        required=False,
        label=_("Access List"),
    )
    index = forms.IntegerField(
        required=False,
        label=_("Index"),
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
        label=_("Action"),
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ACLProtocolChoices),
        required=False,
        label=_("Protocol"),
    )

    # Source selectors
    source_prefix_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("Source Prefix"),
    )

    # Destination selectors
    destination_prefix_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("Destination Prefix"),
    )

    # Tag selector
    tag = TagFilterField(model)
