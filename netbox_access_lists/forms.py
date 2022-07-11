from django import forms

from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, StaticSelectMultiple, TagFilterField
from .models import AccessList, AccessListRule, ActionChoices, ProtocolChoices, TypeChoices


class AccessListForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = AccessList
        fields = ('name', 'type', 'default_action', 'comments', 'tags')


class AccessListFilterForm(NetBoxModelFilterSetForm):
    model = AccessList
    type = forms.MultipleChoiceField(
        choices=TypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    default_action = forms.MultipleChoiceField(
        choices=ActionChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)


class AccessListRuleForm(NetBoxModelForm):
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all()
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all()
    )
    destination_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all()
    )

    class Meta:
        model = AccessListRule
        fields = (
            'access_list', 'index', 'remark', 'source_prefix', 'source_ports', 'destination_prefix',
            'destination_ports', 'protocol', 'action', 'tags',
        )


class AccessListRuleFilterForm(NetBoxModelFilterSetForm):
    model = AccessListRule
    access_list = forms.ModelMultipleChoiceField(
        queryset=AccessList.objects.all(),
        required=False,
        widget=StaticSelectMultiple()
    )
    index = forms.IntegerField(
        required=False
    )
    protocol = forms.MultipleChoiceField(
        choices=ProtocolChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    action = forms.MultipleChoiceField(
        choices=ActionChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)
