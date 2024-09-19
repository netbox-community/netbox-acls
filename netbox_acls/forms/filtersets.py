"""
Defines each django model's GUI filter/search options.
"""
from django.utils.translation import gettext_lazy as _
from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from django import forms
from django.utils.translation import gettext as _
from ipam.models import Prefix
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms.rendering import FieldSet
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
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
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label="Site Group",
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={"region_id": "$region", "group_id": "$site_group"},
    )
    device_id = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            "region_id": "$region",
            "group_id": "$site_group",
            "site_id": "$site",
        },
        required=False,
        label=_("Device",),
    )
    virtual_machine_id = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_("Virtual Machine",)
    )
    virtual_chassis_id = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label=_("Virtual Chassis",)
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ACLTypeChoices),
        required=False,
    )
    default_action = forms.ChoiceField(
        choices=add_blank_choice(ACLActionChoices),
        required=False,
        label="Default Action",
    )
    tag = TagFilterField(model)

    fieldsets = (
        FieldSet("region", "site_group", "site", "device_id", "virtual_chassis_id", "virtual_machine_id", name=_("Host Details")),
        FieldSet("type", "default_action", name=_('ACL Details')),
        FieldSet("q", "tag",name=None)
    )

class ACLInterfaceAssignmentFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter form to search the django AccessList model.
    """

    model = ACLInterfaceAssignment
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label="Site Group",
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={"region_id": "$region", "group_id": "$site_group"},
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            "region_id": "$region",
            "group_id": "$site_group",
            "site_id": "$site",
        },
        required=False,
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            "device_id": "$device",
        },
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Virtual Machine",
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        query_params={
            "virtual_machine_id": "$virtual_machine",
        },
        label="Interface",
    )
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "assigned_object": "$device",
        },
        label="Access List",
    )
    direction = forms.ChoiceField(
        choices=add_blank_choice(ACLAssignmentDirectionChoices),
        required=False,
    )
    tag = TagFilterField(model)

    # fieldsets = (
    #    (None, ('q', 'tag')),
    #    ('Host Details', ('region', 'site_group', 'site', 'device')),
    #    ('ACL Details', ('type', 'default_action')),
    # )


class ACLStandardRuleFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter form to search the django ACLStandardRule model.
    """

    model = ACLStandardRule
    tag = TagFilterField(model)
    access_list = DynamicModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
    )
    source_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Source Prefix",
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
    )

    fieldsets = (
        FieldSet("access_list", "action", "source_prefix", name=_('Rule Details')),
        FieldSet("q", "tag",name=None)
    )
class ACLExtendedRuleFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter form to search the django ACLExtendedRule model.
    """

    model = ACLExtendedRule
    index = forms.IntegerField(
        required=False,
    )
    tag = TagFilterField(model)
    access_list = DynamicModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
    )
    source_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Source Prefix",
    )
    desintation_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Destination Prefix",
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ACLProtocolChoices),
        required=False,
    )

    fieldsets = (
        FieldSet("access_list", "action", "source_prefix", "desintation_prefix", "protocol", name=_('Rule Details')),
        FieldSet("q", "tag",name=None)
    )
