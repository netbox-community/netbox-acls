"""
Defines each django model's GUI filter/search options.
"""

from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import (
    ChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
    add_blank_choice,
)
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
    BaseACLRule,
)

__all__ = (
    "AccessListFilterForm",
    "ACLInterfaceAssignmentFilterForm",
    "ACLStandardRuleFilterForm",
    "ACLExtendedRuleFilterForm",
)


class BaseACLFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter inherited base form to search the django ACL and ACL Interface Assignment models.
    """

    class Meta:
        """
        Sets the parent class as an abstract class to be inherited by other classes.
        """

        abstract = True

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
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            "region_id": "$region",
            "group_id": "$site_group",
            "site_id": "$site",
        },
        required=False,
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
    )


class AccessListFilterForm(BaseACLFilterForm):
    """
    GUI filter form to search the django AccessList model.
    """

    model = AccessList
    virtual_chassis = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
    )
    type = ChoiceField(
        choices=add_blank_choice(ACLTypeChoices),
        required=False,
    )
    default_action = ChoiceField(
        choices=add_blank_choice(ACLActionChoices),
        required=False,
        label="Default Action",
    )
    tag = TagFilterField(model)

    fieldsets = (
        (None, ("q", "tag")),
        (
            "Host Details",
            (
                "region",
                "site_group",
                "site",
                "device",
                "virtual_machine",
                "virtual_chassis",
            ),
        ),
        ("ACL Details", ("type", "default_action")),
    )


class ACLInterfaceAssignmentFilterForm(BaseACLFilterForm):
    """
    GUI filter form to search the django AccessList model.
    """

    model = ACLInterfaceAssignment
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            "device_id": "$device",
        },
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        query_params={
            "virtual_machine_id": "$virtual_machine",
        },
        label="VM Interface",
    )
    direction = ChoiceField(
        choices=add_blank_choice(ACLAssignmentDirectionChoices),
        required=False,
    )
    tag = TagFilterField(model)

    fieldsets = (
        (None, ("q", "tag")),
        (
            "Host Details",
            (
                "region",
                "site_group",
                "site",
                "device",
                "virtual_machine",
            ),
        ),
        ("Interface Details", ("interface", "vminterface")),
    )


class BaseACLRuleFilterForm(NetBoxModelFilterSetForm):
    """
    GUI filter inherited base form to search the django ACL rule models.
    """

    class Meta:
        """
        Sets the parent class as an abstract class to be inherited by other classes.
        """

        abstract = True

    model = BaseACLRule
    index = forms.IntegerField(
        required=False,
    )
    access_list = DynamicModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
    )
    action = ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
    )
    source_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Source Prefix",
    )
    fieldsets = (
        (None, ("q", "tag")),
        ("Rule Details", ("access_list", "action", "source_prefix")),
    )


class ACLStandardRuleFilterForm(BaseACLRuleFilterForm):
    """
    GUI filter form to search the django ACLStandardRule model.
    """

    model = ACLStandardRule

    tag = TagFilterField(model)


class ACLExtendedRuleFilterForm(BaseACLRuleFilterForm):
    """
    GUI filter form to search the django ACLExtendedRule model.
    """

    model = ACLExtendedRule
    tag = TagFilterField(model)
    destination_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Destination Prefix",
    )
    protocol = ChoiceField(
        choices=add_blank_choice(ACLProtocolChoices),
        required=False,
    )
    fieldsets = BaseACLRuleFilterForm.fieldsets + (
        (
            "Rule Details",
            (
                "destination_prefix",
                "protocol",
            ),
        ),
    )
