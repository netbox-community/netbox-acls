"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from dcim.models import (Device, Interface, Region, Site, SiteGroup,
                         VirtualChassis)
from django import forms
from django.utils.safestring import mark_safe
from extras.models import Tag
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm
from utilities.forms import (CommentField, DynamicModelChoiceField,
                             DynamicModelMultipleChoiceField)
from virtualization.models import VirtualMachine, VMInterface

from ..models import (AccessList, ACLExtendedRule, ACLInterfaceAssignment,
                      ACLStandardRule)

__all__ = (
    'AccessListForm',
    'ACLInterfaceAssignmentForm',
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
        required=False,
        query_params={
            'region': '$region',
            'group_id': '$site_group',
            'site_id': '$site',
        },
    )
    virtual_chassis = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label='Virtual Chassis',
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Virtual Machine',
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = AccessList
        fields = ('region', 'site_group', 'site', 'device', 'virtual_machine', 'virtual_chassis', 'name', 'type', 'default_action', 'comments', 'tags')
        help_texts = {
            'default_action': 'The default behavior of the ACL.',
            'name': 'The name uniqueness per device is case insensitive.',
            'type': mark_safe('<b>*Note:</b> CANNOT be changed if ACL Rules are assoicated to this Access List.'),
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance:
            if type(instance.assigned_object) is Device:
                initial['device'] = instance.assigned_object
            elif type(instance.assigned_object) is VirtualChassis:
                initial['virtual_chassis'] = instance.assigned_object
            elif type(instance.assigned_object) is VirtualMachine:
                initial['virtual_machine'] = instance.assigned_object
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validates form inputs before submitting.
        """
        cleaned_data = super().clean()
        error_message = {}
        if self.errors.get('name'):
            return cleaned_data
        name = cleaned_data.get('name')
        type =  cleaned_data.get('type')
        device = cleaned_data.get('device')
        virtual_chassis = cleaned_data.get('virtual_chassis')
        virtual_machine = cleaned_data.get('virtual_machine')
        if (device and virtual_chassis) or (device and virtual_machine) or (virtual_chassis and virtual_machine):
            raise forms.ValidationError('Access Lists must be assigned to one host (either a device, virtual chassis or virtual machine).')
        if not device and not virtual_chassis and not virtual_machine:
            raise forms.ValidationError('Access Lists must be assigned to a device, virtual chassis or virtual machine.')
        if ('name' in self.changed_data or 'device' in self.changed_data) and device and AccessList.objects.filter(name__iexact=name, device=device).exists():
            error_message.update(
                {
                    'device': ['An ACL with this name (case insensitive) is already associated to this host.'],
                    'name': ['An ACL with this name (case insensitive) is already associated to this host.'],
                }
            )
        if ('name' in self.changed_data or 'virtual_chassis' in self.changed_data) and virtual_chassis and AccessList.objects.filter(name__iexact=name, virtual_chassis=virtual_chassis).exists():
            error_message.update(
                {
                    'virtual_chassis': ['An ACL with this name (case insensitive) is already associated to this host.'],
                    'name': ['An ACL with this name (case insensitive) is already associated to this host.'],
                }
            )
        if ('name' in self.changed_data or 'virtual_machine' in self.changed_data) and virtual_machine and AccessList.objects.filter(name__iexact=name, virtual_machine=virtual_machine).exists():
            error_message.update(
                {
                    'virtual_machine': ['An ACL with this name (case insensitive) is already associated to this host.'],
                    'name': ['An ACL with this name (case insensitive) is already associated to this host.'],
                }
            )
        if type == 'extended' and self.instance.aclstandardrules.exists():
            error_message.update({'type': ['This ACL has Standard ACL rules already associated, CANNOT change ACL type!!']})
        elif type == 'standard' and self.instance.aclextendedrules.exists():
            error_message.update({'type': ['This ACL has Extended ACL rules already associated, CANNOT change ACL type!!']})
        if len(error_message) > 0:
            raise forms.ValidationError(error_message)

        return cleaned_data

    def save(self, *args, **kwargs):
        # Set assigned object
        self.instance.assigned_object = self.cleaned_data.get('device') or self.cleaned_data.get('virtual_chassis') or self.cleaned_data.get('virtual_machine')

        return super().save(*args, **kwargs)


class ACLInterfaceAssignmentForm(NetBoxModelForm):
    """
    GUI form to add or edit ACL Host Object assignments
    Requires an access_list, a name, a type, and a default_action.
    """
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
           # Need to pass ACL device to it
        },
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Virtual Machine',
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        query_params={
            'virtual_machine_id': '$virtual_machine'
        },
        label='VM Interface'
    )
    #virtual_chassis = DynamicModelChoiceField(
    #    queryset=VirtualChassis.objects.all(),
    #    required=False,
    #    label='Virtual Chassis',
    #)
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            'assigned_object': '$device',
            #'assigned_object': '$virtual_machine',
        },
        label='Access List',
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    #fieldsets = (
    #    ('Access List Details', ('access_list', 'description', 'tags')),
    #    ('Rule Definition', ('index', 'action', 'remark', 'source_prefix')),
    #)

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance:
            if type(instance.assigned_object) is Interface:
                initial['interface'] = instance.assigned_object
                initial['device'] = 'device'
            elif type(instance.assigned_object) is VMInterface:
                initial['vminterface'] = instance.assigned_object
                initial['virtual_machine'] = 'virtual_machine'
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)


    class Meta:
        model = ACLInterfaceAssignment
        fields = (
            'access_list', 'direction', 'device', 'interface', 'virtual_machine',
            'vminterface', 'comments', 'tags',
        )
        #help_texts = {
        #    'index': 'Determines the order of the rule in the ACL processing.',
        #    'remark': mark_safe('<b>*Note:</b> CANNOT be set if source prefix OR action is set.'),
        #}

    #def clean(self):
    #    """
    #    Validates form inputs before submitting.
    #    If action is set to remark, remark needs to be set.
    #    If action is set to remark, source_prefix cannot be set.
    #    If action is not set to remark, remark cannot be set.
    #    """
    #    cleaned_data = super().clean()
    #    error_message = {}
    #    if cleaned_data.get('action') == 'remark':
    #        if cleaned_data.get('remark') is None:
    #            error_message.update({'remark': ['Action is set to remark, you MUST add a remark.']})
    #        if cleaned_data.get('source_prefix'):
    #            error_message.update({'source_prefix': ['Action is set to remark, Source Prefix CANNOT be set.']})
    #    elif cleaned_data.get('remark'):
    #            error_message.update({'remark': ['CANNOT set remark unless action is set to remark, .']})
    #    if len(error_message) > 0:
    #        raise forms.ValidationError(error_message)
    #    return cleaned_data

    def save(self, *args, **kwargs):
        # Set assigned object
        self.instance.assigned_object = self.cleaned_data.get('interface') or self.cleaned_data.get('vminterface')

        return super().save(*args, **kwargs)


class ACLStandardRuleForm(NetBoxModelForm):
    """
    GUI form to add or edit Standard Access List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            'type': 'standard'
        },
        help_text=mark_safe('<b>*Note:</b> This field will only display Standard ACLs.'),
        label='Access List',
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
        ('Access List Details', ('access_list', 'description', 'tags')),
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
    GUI form to add or edit Extended Access List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            'type': 'extended'
        },
        help_text=mark_safe('<b>*Note:</b> This field will only display Extended ACLs.'),
        label='Access List',
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
        ('Access List Details', ('access_list', 'description', 'tags')),
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
