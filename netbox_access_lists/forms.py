from django import forms
from django.core.exceptions import ValidationError

from extras.models import Tag
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, StaticSelectMultiple, TagFilterField
from .models import AccessList, AccessListExtendedRule, AccessListActionChoices, AccessListProtocolChoices, AccessListTypeChoices, AccessListStandardRule


class AccessListForm(NetBoxModelForm):
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = AccessList
        fields = ('name', 'device', 'type', 'default_action', 'comments', 'tags')

    #def validate_unique(self, value):
    #    accesslists = AccessList.objects.exclude(pk=self.pk)
    #    if accesslists.filter(name=self.name, device=self.device).exists():
    #        raise ValidationError({
    #            "name": f"An Access List with this name on device {self.device} already exists."
    #        })

    def clean(self):
        cleaned_data = super().clean()
        if self.errors.get('name'):
            return cleaned_data
        name = cleaned_data.get('name')
        device = cleaned_data.get('device')
        if ('name' in self.changed_data or 'device' in self.changed_data) and AccessList.objects.filter(name__iexact=name, device=device).exists():
            raise forms.ValidationError('An Access-List with this name on this device already exists.')
        return cleaned_data

class AccessListFilterForm(NetBoxModelFilterSetForm):
    model = AccessList
    type = forms.MultipleChoiceField(
        choices=AccessListTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    default_action = forms.MultipleChoiceField(
        choices=AccessListActionChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)


class AccessListStandardRuleForm(NetBoxModelForm):
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            'type': 'standard'
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False
    )


    class Meta:
        model = AccessListStandardRule
        fields = (
            'access_list', 'index', 'remark', 'action', 'tags', 'source_prefix',
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('remark'):
            if cleaned_data.get('action'):
                raise forms.ValidationError('Cannot input a remark AND an action. Remove one.')
            if cleaned_data.get('source_prefix'):
                raise forms.ValidationError('Cannot input a remark AND a source prefix. Remove one.')
        #if cleaned_data.get('access_list_type') == 'standard' and (source_ports or destination_prefix or destination_ports):
        #    raise forms.ValidationError('Standard Access-Lists only allow a source_prefix or remark')
        return cleaned_data


class AccessListStandardRuleFilterForm(NetBoxModelFilterSetForm):
    model = AccessListStandardRule
    access_list = forms.ModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
        widget=StaticSelectMultiple()
    )
    index = forms.IntegerField(
        required=False
    )
    tag = TagFilterField(model)
    action = forms.MultipleChoiceField(
        choices=AccessListActionChoices,
        required=False,
        widget=StaticSelectMultiple()
    )


class AccessListExtendedRuleForm(NetBoxModelForm):
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            'type': 'extended'
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False
    )
    destination_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False
    )


    class Meta:
        model = AccessListExtendedRule
        fields = (
            'access_list', 'index', 'remark', 'action', 'tags', 'source_prefix',
            'source_ports', 'destination_prefix', 'destination_ports', 'protocol'
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('remark'):
            if cleaned_data.get('action'):
                raise forms.ValidationError('Cannot input a remark AND an action. Remove one.')
            if cleaned_data.get('source_prefix'):
                raise forms.ValidationError('Cannot input a remark AND a source prefix. Remove one.')
            if cleaned_data.get('source_ports'):
                raise forms.ValidationError('Cannot input a remark AND source ports. Remove one.')
            if cleaned_data.get('destination_prefix'):
                raise forms.ValidationError('Cannot input a remark AND a destination prefix. Remove one.')
            if cleaned_data.get('destination_ports'):
                raise forms.ValidationError('Cannot input a remark AND destination ports. Remove one.')
            if cleaned_data.get('protocol'):
                raise forms.ValidationError('Cannot input a remark AND a protocol. Remove one.')
        #if cleaned_data.get('access_list_type') == 'standard' and (source_ports or destination_prefix or destination_ports):
        #    raise forms.ValidationError('Standard Access-Lists only allow a source_prefix or remark')
        return cleaned_data


class AccessListExtendedRuleFilterForm(NetBoxModelFilterSetForm):
    model = AccessListExtendedRule
    access_list = forms.ModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
        widget=StaticSelectMultiple()
    )
    index = forms.IntegerField(
        required=False
    )
    tag = TagFilterField(model)
    action = forms.MultipleChoiceField(
        choices=AccessListActionChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    protocol = forms.MultipleChoiceField(
        choices=AccessListProtocolChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
