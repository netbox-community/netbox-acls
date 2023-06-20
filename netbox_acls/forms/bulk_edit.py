"""
Draft for a possible BulkEditForm, but may not be worth wile.
"""

# from dcim.models import Device, Region, Site, SiteGroup, VirtualChassis
# from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.safestring import mark_safe
# from netbox.forms import NetBoxModelBulkEditForm
# from utilities.forms.utils import add_blank_choice
# from utilities.forms.fields import (
#     ChoiceField,
#     DynamicModelChoiceField,
#     StaticSelect,
# )
# from virtualization.models import VirtualMachine

# from ..choices import ACLActionChoices, ACLTypeChoices
# from ..models import AccessList


# __all__ = (
#    'AccessListBulkEditForm',
# )


# class AccessListBulkEditForm(NetBoxModelBulkEditForm):
#    model = AccessList
#
#    region = DynamicModelChoiceField(
#        queryset=Region.objects.all(),
#        required=False,
#    )
#    site_group = DynamicModelChoiceField(
#        queryset=SiteGroup.objects.all(),
#        required=False,
#        label='Site Group'
#    )
#    site = DynamicModelChoiceField(
#        queryset=Site.objects.all(),
#        required=False
#    )
#    device = DynamicModelChoiceField(
#        queryset=Device.objects.all(),
#        query_params={
#            'region': '$region',
#            'group_id': '$site_group',
#            'site_id': '$site',
#        },
#        required=False,
#    )
#    type = ChoiceField(
#        choices=add_blank_choice(ACLTypeChoices),
#        required=False,
#        widget=StaticSelect(),
#    )
#    default_action = ChoiceField(
#        choices=add_blank_choice(ACLActionChoices),
#        required=False,
#        widget=StaticSelect(),
#        label='Default Action',
#    )
#
#    fieldsets = [
#        ('Host Details', ('region', 'site_group', 'site', 'device')),
#        ('Access List Details', ('type', 'default_action', 'add_tags', 'remove_tags')),
#    ]
#
#
#    class Meta:
#        model = AccessList
#        fields = ('region', 'site_group', 'site', 'device', 'type', 'default_action', 'add_tags', 'remove_tags')
#        help_texts = {
#            'default_action': 'The default behavior of the ACL.',
#            'name': 'The name uniqueness per device is case insensitive.',
#            'type': mark_safe('<b>*Note:</b> CANNOT be changed if ACL Rules are assoicated to this Access List.'),
#        }
#
#    def clean(self): # Not working given you are bulkd editing multiple forms
#        cleaned_data = super().clean()
#        if self.errors.get('name'):
#            return cleaned_data
#        name = cleaned_data.get('name')
#        device = cleaned_data.get('device')
#        type = cleaned_data.get('type')
#        if ('name' in self.changed_data or 'device' in self.changed_data) and AccessList.objects.filter(name__iexact=name, device=device).exists():
#            raise forms.ValidationError('An ACL with this name (case insensitive) is already associated to this device.')
#        if type == 'extended' and self.cleaned_data['aclstandardrules'].exists():
#            raise forms.ValidationError('This ACL has Standard ACL rules already associated, CANNOT change ACL type!!')
#        elif type == 'standard' and self.cleaned_data['aclextendedrules'].exists():
#            raise forms.ValidationError('This ACL has Extended ACL rules already associated, CANNOT change ACL type!!')
#        return cleaned_data
