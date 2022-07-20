"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from dcim.models import Device, Region, Site, SiteGroup
from django import forms
from django.utils.safestring import mark_safe
from extras.models import Tag
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm
from utilities.forms import (CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField)

from netbox_access_lists.models import (AccessList, ACLExtendedRule, ACLStandardRule)

__all__ = (
    'AccessListForm',
    'ACLStandardRuleForm',
    'ACLExtendedRuleForm',
)

# Sets a standard mark_save help_text value to be used by the various classes
acl_rule_logic_help = mark_safe('<b>*Note:</b> CANNOT be set if action is set to remark.')


class AccessListForm(NetBoxModelForm):
    """
    GUI form to add or edit an AccessList.
    Requires a device, a name, a type, and a default_action.
    """
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Site Group'
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'region': '$region',
            'group_id': '$site_group',
            'site_id': '$site',
        },
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = [
        ('Host Details', ('region', 'site_group', 'site', 'device')),
        ('Access-List Details', ('name', 'type', 'default_action', 'tags')),
    ]

    class Meta:
        model = AccessList
        fields = ('region', 'site_group', 'site', 'device', 'name', 'type', 'default_action', 'comments', 'tags')
        help_texts = {
            'default_action': 'The default behavior of the ACL.',
            'name': 'The name uniqueness per device is case insensitive.',
            'type': mark_safe('<b>*Note:</b> CANNOT be changed if ACL Rules are assoicated to this Access-List.'),
        }

    def clean(self):
        """
        Validates form inputs before submitting.
        """
        cleaned_data = super().clean()
        error_message = {}
        if self.errors.get('name'):
            return cleaned_data
        name = cleaned_data.get('name')
        device = cleaned_data.get('device')
        type =  cleaned_data.get('type')
        if ('name' in self.changed_data or 'device' in self.changed_data) and AccessList.objects.filter(name__iexact=name, device=device).exists():
            error_message.update(
                {
                    'device': ['An ACL with this name (case insensitive) is already associated to this device.'],
                    'name': ['An ACL with this name (case insensitive) is already associated to this device.']
                }
                )
        if type == 'extended' and self.instance.aclstandardrules.exists():
            error_message.update({'type': ['This ACL has Standard ACL rules already associated, CANNOT change ACL type!!']})
        elif type == 'standard' and self.instance.aclextendedrules.exists():
            error_message.update({'type': ['This ACL has Extended ACL rules already associated, CANNOT change ACL type!!']})
        if len(error_message) > 0:
            raise forms.ValidationError(error_message)

        return cleaned_data


class ACLStandardRuleForm(NetBoxModelForm):
    """
    GUI form to add or edit Standard Access-List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            'type': 'standard'
        },
        help_text=mark_safe('<b>*Note:</b> This field will only display Standard ACLs.'),
        label='Access-List',
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text=acl_rule_logic_help,
        label='Source Prefix',
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Access-List Details', ('access_list', 'description', 'tags')),
        ('Rule Definition', ('index', 'action', 'remark', 'source_prefix')),
    )

    class Meta:
        model = ACLStandardRule
        fields = (
            'access_list', 'index', 'action', 'remark', 'source_prefix',
            'tags', 'description'
        )
        help_texts = {
            'index': 'Determines the order of the rule in the ACL processing.',
            'remark': mark_safe('<b>*Note:</b> CANNOT be set if source prefix OR action is set.'),
        }

    def clean(self):
        """
        Validates form inputs before submitting.
        If action is set to remark, remark needs to be set.
        If action is set to remark, source_prefix cannot be set.
        If action is not set to remark, remark cannot be set.
        """
        cleaned_data = super().clean()
        error_message = {}
        if cleaned_data.get('action') == 'remark':
            if cleaned_data.get('remark') is None:
                error_message.update({'remark': ['Action is set to remark, you MUST add a remark.']})
            if cleaned_data.get('source_prefix'):
                error_message.update({'source_prefix': ['Action is set to remark, Source Prefix CANNOT be set.']})
        elif cleaned_data.get('remark'):
                error_message.update({'remark': ['CANNOT set remark unless action is set to remark, .']})
        if len(error_message) > 0:
            raise forms.ValidationError(error_message)
        return cleaned_data


class ACLExtendedRuleForm(NetBoxModelForm):
    """
    GUI form to add or edit Extended Access-List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            'type': 'extended'
        },
        help_text=mark_safe('<b>*Note:</b> This field will only display Extended ACLs.'),
        label='Access-List',
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text=acl_rule_logic_help,
        label='Source Prefix',
    )
    destination_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text=acl_rule_logic_help,
        label='Destination Prefix',
    )
    fieldsets = (
        ('Access-List Details', ('access_list', 'description', 'tags')),
        ('Rule Definition', ('index', 'action', 'remark', 'source_prefix', 'source_ports', 'destination_prefix', 'destination_ports', 'protocol',)),
    )

    class Meta:
        model = ACLExtendedRule
        fields = (
            'access_list', 'index', 'action', 'remark', 'source_prefix',
            'source_ports', 'destination_prefix', 'destination_ports', 'protocol',
            'tags', 'description'
        )
        help_texts = {
            'destination_ports': acl_rule_logic_help,
            'index': 'Determines the order of the rule in the ACL processing.',
            'protocol': acl_rule_logic_help,
            'remark': mark_safe('<b>*Note:</b> CANNOT be set if action is not set to remark.'),
            'source_ports': acl_rule_logic_help,
        }

    def clean(self):
        """
        Validates form inputs before submitting.
        If action is set to remark, remark needs to be set.
        If action is set to remark, source_prefix, source_ports, desintation_prefix, destination_ports, or protocol cannot be set.
        If action is not set to remark, remark cannot be set.
        """
        cleaned_data = super().clean()
        error_message = {}
        if cleaned_data.get('action') == 'remark':
            if cleaned_data.get('remark') is None:
                error_message.update({'remark': ['Action is set to remark, you MUST add a remark.']})
            if cleaned_data.get('source_prefix'):
                error_message.update({'source_prefix': ['Action is set to remark, Source Prefix CANNOT be set.']})
            if cleaned_data.get('source_ports'):
                error_message.update({'source_ports': ['Action is set to remark, Source Ports CANNOT be set.']})
            if cleaned_data.get('destination_prefix'):
                error_message.update({'destination_prefix': ['Action is set to remark, Destination Prefix CANNOT be set.']})
            if cleaned_data.get('destination_ports'):
                error_message.update({'destination_ports': ['Action is set to remark, Destination Ports CANNOT be set.']})
            if cleaned_data.get('protocol'):
                error_message.update({'protocol': ['Action is set to remark, Protocol CANNOT be set.']})
        elif cleaned_data.get('remark'):
                error_message.update({'remark': ['CANNOT set remark unless action is set to remark, .']})
        if len(error_message) > 0:
            raise forms.ValidationError(error_message)
        return cleaned_data
