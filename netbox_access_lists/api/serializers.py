"""
Serializers control the translation of client data to and from Python objects,
while Django itself handles the database abstraction.
"""

from django.contrib.contenttypes.models import ContentType
from drf_yasg.utils import swagger_serializer_method
from ipam.api.serializers import NestedPrefixSerializer
from django.core.exceptions import ObjectDoesNotExist
from netbox.api import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from utilities.api import get_serializer_for_model

from ..constants import (ACL_HOST_ASSIGNMENT_MODELS,
                         ACL_INTERFACE_ASSIGNMENT_MODELS)
from ..models import (AccessList, ACLExtendedRule, ACLInterfaceAssignment,
                      ACLStandardRule)
from .nested_serializers import (NestedAccessListSerializer,
                                 NestedACLExtendedRuleSerializer,
                                 NestedACLInterfaceAssignmentSerializer,
                                 NestedACLStandardRuleSerializer)

__all__ = [
    'AccessListSerializer',
    'ACLInterfaceAssignmentSerializer',
    'ACLStandardRuleSerializer',
    'ACLExtendedRuleSerializer'
]

# Sets a standard error message for ACL rules with an action of remark, but no remark set.
error_message_no_remark = 'Action is set to remark, you MUST add a remark.'
# Sets a standard error message for ACL rules with an action of remark, but no source_prefix is set.
error_message_action_remark_source_prefix_set = 'Action is set to remark, Source Prefix CANNOT be set.'
# Sets a standard error message for ACL rules with an action not set to remark, but no remark is set.
error_message_remark_without_action_remark = 'CANNOT set remark unless action is set to remark.'
# Sets a standard error message for ACL rules no associated to an ACL of the same type.
error_message_acl_type = 'Provided parent Access List is not of right type.'


class AccessListSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django AccessList model & associates it to a view.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:accesslist-detail'
    )
    rule_count = serializers.IntegerField(read_only=True)
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(ACL_HOST_ASSIGNMENT_MODELS)
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Associates the django model AccessList & fields to the serializer.
        """
        model = AccessList
        fields = (
            'id', 'url', 'display', 'name', 'assigned_object_type', 'assigned_object_id', 'assigned_object', 'type', 'default_action', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'rule_count'
        )

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_assigned_object(self, obj):
        serializer = get_serializer_for_model(obj.assigned_object, prefix='Nested')
        context = {'request': self.context['request']}
        return serializer(obj.assigned_object, context=context).data

    def validate(self, data):
        """
        Validates api inputs before processing:
          - Check if Access List has no existing rules before change the Access List's type.
        """

        # Validate that the parent object exists
        if 'assigned_object_type' in data and 'assigned_object_id' in data:
            try:
                assigned_object = data['assigned_object_type'].get_object_for_this_type(id=data['assigned_object_id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Invalid assigned_object: {data['assigned_object_type']} ID {data['assigned_object_id']}"
                )

        # Check if Access List has no existing rules before change the Access List's type.
        if self.instance and self.instance.type != data.get('type') and self.instance.rule_count > 0:
            error_message['type'] = ['This ACL has ACL rules associated, CANNOT change ACL type.']

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)


class ACLInterfaceAssignmentSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django ACLInterfaceAssignment model & associates it to a view.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:aclinterfaceassignment-detail'
    )
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(ACL_INTERFACE_ASSIGNMENT_MODELS)
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Associates the django model ACLInterfaceAssignment & fields to the serializer.
        """
        model = ACLInterfaceAssignment
        fields = (
            'id', 'url', 'access_list', 'direction', 'assigned_object_type', 'assigned_object_id', 'assigned_object', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated'
        )

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_assigned_object(self, obj):
        serializer = get_serializer_for_model(obj.assigned_object, prefix='Nested')
        context = {'request': self.context['request']}
        return serializer(obj.assigned_object, context=context).data

    def validate(self, data):
        """
        Validate the AccessList django model model's inputs before allowing it to update the instance.
        """
        error_message = {}

        # Validate that the parent object exists
        if 'assigned_object_type' in data and 'assigned_object_id' in data:
            try:
                assigned_object = data['assigned_object_type'].get_object_for_this_type(id=data['assigned_object_id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Invalid assigned_object: {data['assigned_object_type']} ID {data['assigned_object_id']}"
                )
            if data['assigned_object_type'].model == 'interface':
                error_message['access_list'] = [assigned_object.device]
            elif data['assigned_object_type'].model == 'vminterface':
                error_message['access_list'] = [assigned_object.virtual_machine]

        #get the parent ACL host id and host type and check

        #assigned_object_type = data.get('assigned_object_type')
        #assigned_object_type_id = ContentType.objects.get_for_model(assigned_object_type).pk
        #assigned_object_id = data.get('assigned_object_id')
        #access_list = data.get('access_list')



        # Check if Access List has no existing rules before change the Access List's type.
        #if self.instance and self.instance.type != data.get('type') and self.instance.rule_count > 0:
        #    error_message['type'] = ['This ACL has ACL rules associated, CANNOT change ACL type.']

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)

class ACLStandardRuleSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django ACLStandardRule model & associates it to a view.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:aclstandardrule-detail'
    )
    access_list = NestedAccessListSerializer()
    source_prefix = NestedPrefixSerializer(
        required=False,
        allow_null=True,
        default=None
    )

    class Meta:
        """
        Associates the django model ACLStandardRule & fields to the serializer.
        """
        model = ACLStandardRule
        fields = (
            'id', 'url', 'display', 'access_list', 'index', 'action', 'tags', 'description',
            'remark', 'created', 'custom_fields', 'last_updated', 'source_prefix'
        )

    def validate(self, data):
        """
        Validate the ACLStandardRule django model model's inputs before allowing it to update the instance.
        """
        error_message = {}

        # Check if action set to remark, but no remark set.
        if data.get('action') == 'remark' and data.get('remark') is None:
            error_message['remark'] = [error_message_no_remark]
        # Check if action set to remark, but source_prefix set.
        if data.get('source_prefix'):
            error_message['source_prefix'] = [error_message_action_remark_source_prefix_set]

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)


class ACLExtendedRuleSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django ACLExtendedRule model & associates it to a view.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_access_lists-api:aclextendedrule-detail'
    )
    access_list = NestedAccessListSerializer()
    source_prefix = NestedPrefixSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    destination_prefix = NestedPrefixSerializer(
        required=False,
        allow_null=True,
        default=None
    )

    class Meta:
        """
        Associates the django model ACLExtendedRule & fields to the serializer.
        """
        model = ACLExtendedRule
        fields = (
            'id', 'url', 'display', 'access_list', 'index', 'action', 'tags', 'description',
            'created', 'custom_fields', 'last_updated', 'source_prefix', 'source_ports',
            'destination_prefix', 'destination_ports', 'protocol', 'remark',
        )

    def validate(self, data):
        """
        Validate the ACLExtendedRule django model model's inputs before allowing it to update the instance.
        """
        error_message = {}

        # Check if action set to remark, but no remark set.
        if data.get('action') == 'remark' and data.get('remark') is None:
            error_message['remark'] = [error_message_no_remark]
        # Check if action set to remark, but source_prefix set.
        if data.get('source_prefix'):
            error_message['source_prefix'] = [error_message_action_remark_source_prefix_set]
        # Check if action set to remark, but source_ports set.
        if data.get('source_ports'):
            error_message['source_ports'] = ['Action is set to remark, Source Ports CANNOT be set.']
        # Check if action set to remark, but destination_prefix set.
        if data.get('destination_prefix'):
            error_message['destination_prefix'] = ['Action is set to remark, Destination Prefix CANNOT be set.']
        # Check if action set to remark, but destination_ports set.
        if data.get('destination_ports'):
            error_message['destination_ports'] = ['Action is set to remark, Destination Ports CANNOT be set.']
        # Check if action set to remark, but protocol set.
        if data.get('protocol'):
            error_message['protocol'] = ['Action is set to remark, Protocol CANNOT be set.']

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)
