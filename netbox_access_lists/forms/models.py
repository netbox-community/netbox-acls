"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from dcim.models import (Device, Interface, Region, Site, SiteGroup,
                         VirtualChassis)
from django import forms
from django.contrib.contenttypes.models import ContentType
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
        acl_type = cleaned_data.get('type')
        device = cleaned_data.get('device')
        virtual_chassis = cleaned_data.get('virtual_chassis')
        virtual_machine = cleaned_data.get('virtual_machine')


        if (device and virtual_chassis) or (device and virtual_machine) or (virtual_chassis and virtual_machine):
            raise forms.ValidationError('Access Lists must be assigned to one host (either a device, virtual chassis or virtual machine) at a time.')
        if not device and not virtual_chassis and not virtual_machine:
            raise forms.ValidationError('Access Lists must be assigned to a device, virtual chassis or virtual machine.')

        if device:
            host_type = 'device'
        elif virtual_chassis:
            host_type = 'virtual_chassis'
        elif virtual_machine:
            host_type = 'virtual_machine'
        if ('name' in self.changed_data or host_type in self.changed_data) and AccessList.objects.filter(name__iexact=name, device=device).exists():
            error_same_acl_name = 'An ACL with this name (case insensitive) is already associated to this host.'
            error_message |= {host_type: [error_same_acl_name], 'name': [error_same_acl_name]}

        if acl_type == 'extended' and self.instance.aclstandardrules.exists():
            error_message['type'] = ['This ACL has Standard ACL rules already associated, CANNOT change ACL type!!']

        elif acl_type == 'standard' and self.instance.aclextendedrules.exists():
            error_message['type'] = ['This ACL has Extended ACL rules already associated, CANNOT change ACL type!!']

        if error_message:
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
        #query_params={
        #    'assigned_object': '$device',
        #    'assigned_object': '$virtual_machine',
        #},
        label='Access List',
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

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

    def clean(self):
        """
        Validates form inputs before submitting.
        If action is set to remark, remark needs to be set.
        If action is set to remark, source_prefix cannot be set.
        If action is not set to remark, remark cannot be set.
        """
        cleaned_data = super().clean()
        error_message = {}
        access_list = cleaned_data.get('access_list')
        direction = cleaned_data.get('direction')
        interface = cleaned_data.get('interface')
        vminterface = cleaned_data.get('vminterface')
        assigned_object = cleaned_data.get('assigned_object')
        if interface:
            assigned_object_id = Interface.objects.get(pk=interface.pk).pk
            assigned_object_type = 'interface'
            assigned_object_type_id = ContentType.objects.get_for_model(interface).pk
            host = Interface.objects.get(pk=interface.pk).device
            host_object_type_id  = ContentType.objects.get_for_model(host).pk
            host_type = 'device'
        elif vminterface:
            assigned_object_id = VMInterface.objects.get(pk=vminterface.pk).pk
            assigned_object_type = 'vminterface'
            assigned_object_type_id = ContentType.objects.get_for_model(vminterface).pk
            host = VMInterface.objects.get(pk=vminterface.pk).virtual_machine
            host_object_type_id  = ContentType.objects.get_for_model(vminterface).pk
            host_type = 'virtual_machine'
        access_list_host = AccessList.objects.get(pk=access_list.pk).assigned_object

        # Check that both interface and vminterface are not set
        if interface and vminterface:
            error_too_many_interfaces = 'Access Lists must be assigned to one type of interface at a time (VM interface or physical interface)'
            error_too_many_hosts = 'Access Lists must be assigned to one type of device at a time (VM or physical device).'
            error_message |= {'device': [error_too_many_hosts], 'interface': [error_too_many_interfaces], 'virtual_machine': [error_too_many_hosts], 'vminterface': [error_too_many_interfaces]}
        elif not (interface or vminterface):
            error_no_interface = 'An Access List assignment but specify an Interface or VM Interface.'
            error_message |= {'interface': [error_no_interface], 'vminterface': [error_no_interface]}
        # If NOT set with 2 interface types, check that an interface's parent device/virtual_machine is assigned to the Access List.
        elif access_list_host != host:
            error_acl_not_on_host = 'Access Lists must be assigned to a host before it can be assigned to the host interface.'
            error_message |= {'access_list': [error_acl_not_on_host], assigned_object_type: [error_acl_not_on_host], host_type: [error_acl_not_on_host]}

        # Check that for duplicate entry
        if ACLInterfaceAssignment.objects.filter(access_list=access_list, assigned_object_id=assigned_object_id, assigned_object_type=assigned_object_type_id, direction=direction).exists():
            error_duplicate_entry = 'An ACL with this name is already associated to this interface & direction.'
            error_message |= {'access_list': [error_duplicate_entry], 'direction': [error_duplicate_entry], assigned_object_type: [error_duplicate_entry]}
        # Check if ACL assigned to host
        elif not AccessList.objects.filter(assigned_object_id=host.pk, assigned_object_type=host_object_type_id, name=access_list).exists():
            error_acl_not_assigned_to_host = 'Access List not present on selected host.'
            error_message |= {'access_list': [error_acl_not_assigned_to_host], host_type: [error_acl_not_assigned_to_host]}
        # Check that the interface does not have an existing ACL applied in the direction already
        elif ACLInterfaceAssignment.objects.filter(assigned_object_id=assigned_object_id, assigned_object_type=assigned_object_type_id, direction=direction).exists():
            error_interface_already_assigned = 'Interfaces can only have 1 Access List Assigned in each direction.'
            error_message |= {'direction': [error_interface_already_assigned], assigned_object_type: [error_interface_already_assigned]}

        if error_message:
            raise forms.ValidationError(error_message)
        return cleaned_data

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
                error_message['remark'] = ['Action is set to remark, you MUST add a remark.']
            if cleaned_data.get('source_prefix'):
                error_message['source_prefix'] = ['Action is set to remark, Source Prefix CANNOT be set.']
        elif cleaned_data.get('remark'):
                error_message['remark'] = ['CANNOT set remark unless action is set to remark, .']

        if error_message:
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
                error_message['remark'] = ['Action is set to remark, you MUST add a remark.']
            if cleaned_data.get('source_prefix'):
                error_message['source_prefix'] = ['Action is set to remark, Source Prefix CANNOT be set.']
            if cleaned_data.get('source_ports'):
                error_message['source_ports'] = ['Action is set to remark, Source Ports CANNOT be set.']
            if cleaned_data.get('destination_prefix'):
                error_message['destination_prefix'] = ['Action is set to remark, Destination Prefix CANNOT be set.']
            if cleaned_data.get('destination_ports'):
                error_message['destination_ports'] = ['Action is set to remark, Destination Ports CANNOT be set.']
            if cleaned_data.get('protocol'):
                error_message['protocol'] = ['Action is set to remark, Protocol CANNOT be set.']
        elif cleaned_data.get('remark'):
                error_message['remark'] = ['CANNOT set remark unless action is set to remark, .']
        if error_message:
            raise forms.ValidationError(error_message)
        return cleaned_data
