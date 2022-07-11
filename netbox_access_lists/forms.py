from django import forms

from extras.models import Tag
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, StaticSelectMultiple, TagFilterField
from .models import AccessList, AccessListRule, AccessListActionChoices, AccessListProtocolChoices, AccessListTypeChoices


class AccessListForm(NetBoxModelForm):
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = AccessList
        fields = ('name', 'type', 'default_action', 'comments', 'tags')


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
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
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
        choices=AccessListProtocolChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    action = forms.MultipleChoiceField(
        choices=AccessListActionChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)
