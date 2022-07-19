from dcim.models import Device, Region, Site, SiteGroup
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from extras.models import Tag
from ipam.models import Prefix
from netbox.forms import (NetBoxModelBulkEditForm, NetBoxModelFilterSetForm,
                          NetBoxModelForm)
from utilities.forms import (ChoiceField, CommentField,
                             DynamicModelChoiceField,
                             DynamicModelMultipleChoiceField,
                             MultipleChoiceField, StaticSelect,
                             StaticSelectMultiple, TagFilterField,
                             add_blank_choice)

from netbox_access_lists.models import (AccessList, ACLActionChoices, ACLExtendedRule,
                     ACLProtocolChoices, ACLRuleActionChoices, ACLStandardRule,
                     ACLTypeChoices)

__all__ = (
    'AccessListFilterForm',
    'ACLStandardRuleFilterForm',
    'ACLExtendedRuleFilterForm',
)


class AccessListFilterForm(NetBoxModelFilterSetForm):
    model = AccessList
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
        required=False
    )
    type = ChoiceField(
        choices=add_blank_choice(ACLTypeChoices),
        required=False,
        initial='',
        widget=StaticSelect(),
    )
    default_action = ChoiceField(
        choices=add_blank_choice(ACLActionChoices),
        required=False,
        initial='',
        widget=StaticSelect(),
        label='Default Action',
    )
    tag = TagFilterField(model)

    fieldsets = (
        (None, ('q', 'tag')),
        ('Host Details', ('region', 'site_group', 'site', 'device')),
        ('ACL Details', ('type', 'default_action')),
    )


class ACLStandardRuleFilterForm(NetBoxModelFilterSetForm):
    model = ACLStandardRule
    tag = TagFilterField(model)
    source_prefix = forms.ModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        widget=StaticSelectMultiple(),
        label='Source Prefix',
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
        initial='',
        widget=StaticSelect(),
    )
    fieldsets = (
        (None, ('q', 'tag')),
        ('Rule Details', ('action', 'source_prefix',)),
    )


class ACLExtendedRuleFilterForm(NetBoxModelFilterSetForm):
    model = ACLExtendedRule
    index = forms.IntegerField(
        required=False
    )
    tag = TagFilterField(model)
    action = forms.ChoiceField(
        choices=add_blank_choice(ACLRuleActionChoices),
        required=False,
        widget=StaticSelect(),
        initial='',
    )
    source_prefix = forms.ModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        widget=StaticSelectMultiple(),
        label='Source Prefix',
    )
    desintation_prefix = forms.ModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        widget=StaticSelectMultiple(),
        label='Destination Prefix',
    )
    protocol = ChoiceField(
        choices=add_blank_choice(ACLProtocolChoices),
        required=False,
        widget=StaticSelect(),
        initial='',
    )

    fieldsets = (
        (None, ('q', 'tag')),
        ('Rule Details', ('action', 'source_prefix', 'desintation_prefix', 'protocol')),
    )
