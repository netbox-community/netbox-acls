from rest_framework import serializers

from ipam.api.serializers import NestedPrefixSerializer
from dcim.api.serializers import NestedDeviceSerializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from ..models import AccessList, ACLExtendedRule, ACLStandardRule


#
# Nested serializers
#

class NestedAccessListSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:accesslist-detail'
    )

    class Meta:
        model = AccessList
        fields = ('id', 'url', 'display', 'name', 'device')


class NestedACLStandardRuleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:aclstandardrule-detail'
    )

    class Meta:
        model = ACLStandardRule
        fields = ('id', 'url', 'display', 'index')


class NestedACLExtendedRuleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:aclextendedrule-detail'
    )

    class Meta:
        model = ACLExtendedRule
        fields = ('id', 'url', 'display', 'index')


#
# Regular serializers
#

class AccessListSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:accesslist-detail'
    )
    rule_count = serializers.IntegerField(read_only=True)
    device = NestedDeviceSerializer()

    class Meta:
        model = AccessList
        fields = (
            'id', 'url', 'display', 'name', 'device', 'type', 'default_action', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'rule_count'
        )

    def validate(self, data):

        if self.instance.rule_count > 0:
            raise serializers.ValidationError({
                'type': 'This ACL has ACL rules already associated, CANNOT change ACL type!!'
            })

        return super().validate(data)


class ACLStandardRuleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:aclstandardrule-detail'
    )
    access_list = NestedAccessListSerializer()
    source_prefix = NestedPrefixSerializer()

    class Meta:
        model = ACLStandardRule
        fields = (
            'id', 'url', 'display', 'access_list', 'index', 'action', 'tags',
            'created', 'custom_fields', 'last_updated', 'source_prefix'
        )

    def validate(self, data):

        access_list = data.get('access_list')
        if access_list.type == 'extended':
            raise serializers.ValidationError({
                'access_list': 'CANNOT associated standard ACL rules to an extended ACL!!'
            })

        return super().validate(data)


class ACLExtendedRuleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:aclextendedrule-detail'
    )
    access_list = NestedAccessListSerializer()
    source_prefix = NestedPrefixSerializer()
    destination_prefix = NestedPrefixSerializer()

    class Meta:
        model = ACLExtendedRule
        fields = (
            'id', 'url', 'display', 'access_list', 'index', 'action', 'tags',
            'created', 'custom_fields', 'last_updated', 'source_prefix', 'source_ports',
            'destination_prefix', 'destination_ports', 'protocol'
        )

    def validate(self, data):

        access_list = data.get('access_list')
        if access_list.type == 'standard':
            raise serializers.ValidationError({
                'access_list': 'CANNOT associated extended ACL rules to a standard ACL!!'
            })

        return super().validate(data)
