"""
Defines each django model's GUI filter/search options.
"""
from django.utils.translation import gettext_lazy as _
from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from django import forms
from django.utils.translation import gettext as _
from ipam.models import (
    Prefix,
    IPRange,
    IPAddress,
    Aggregate,
    Service,
)
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms.rendering import FieldSet
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.utils import add_blank_choice
from utilities.forms.rendering import FieldSet, TabbedGroups
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
    source_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Source Prefix",
    )
    source_iprange = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Source IP-Range",
    )
    source_ipaddress = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Source IP-Address",
    )
    source_aggregate = DynamicModelMultipleChoiceField(
        queryset=Aggregate.objects.all(),
        required=False,
        label="Source Aggregate",
    )    
    source_service = DynamicModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label="Source Service",
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
    )

    fieldsets = (
        FieldSet("q", "tag",name=None),
        FieldSet(
            "access_list",
            "action",
            name=_('Rule Details')
        ),
        FieldSet(
            TabbedGroups(
                FieldSet('source_prefix', name=_('Prefix')),
                FieldSet('source_iprange', name=_('IP Range')),
                FieldSet('source_ipaddress', name=_('IP Address')),
                FieldSet('source_aggregate', name=_('Aggregate')),
                FieldSet('source_service', name=_('Service')),
            )
        )
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
    source_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Source Prefix",
    )
    source_iprange = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Source IP-Range",
    )
    source_ipaddress = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Source IP-Address",
    )
    source_aggregate = DynamicModelMultipleChoiceField(
        queryset=Aggregate.objects.all(),
        required=False,
        label="Source Aggregate",
    )    
    source_service = DynamicModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label="Source Service",
    )

    destination_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Destination Prefix",
    )
    destination_iprange = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Destination IP-Range",
    )
    destination_ipaddress = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Destination IP-Address",
    )
    destination_aggregate = DynamicModelMultipleChoiceField(
        queryset=Aggregate.objects.all(),
        required=False,
        label="Destination Aggregate",
    )    
    destination_service = DynamicModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label="Destination Service",
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ACLProtocolChoices),
        required=False,
    )

    fieldsets = (
        FieldSet("q", "tag",name=None),
        FieldSet(
            "access_list",
            "action",
            "protocol",
            name=_('Rule Details')
        ),
        FieldSet(
            TabbedGroups(
                FieldSet('source_prefix', name=_('Prefix')),
                FieldSet('source_iprange', name=_('IP Range')),
                FieldSet('source_ipaddress', name=_('IP Address')),
                FieldSet('source_aggregate', name=_('Aggregate')),
                FieldSet('source_service', name=_('Service')),
            ),
            "source_ports",
        ),
        FieldSet(
            TabbedGroups(
                FieldSet('destination_prefix', name=_('Prefix')),
                FieldSet('destination_iprange', name=_('IP Range')),
                FieldSet('destination_ipaddress', name=_('IP Address')),
                FieldSet('destination_aggregate', name=_('Aggregate')),
                FieldSet('destination_service', name=_('Service')),
            ),
            "destination_ports",
        ),
    )
