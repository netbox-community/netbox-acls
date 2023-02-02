"""
Serializers control the translation of client data to and from Python objects,
while Django itself handles the database abstraction.
"""

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_serializer_method
from ipam.api.serializers import NestedPrefixSerializer
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from netbox.constants import NESTED_SERIALIZER_PREFIX
from rest_framework import serializers
from utilities.api import get_serializer_for_model

from ..constants import ACL_HOST_ASSIGNMENT_MODELS, ACL_INTERFACE_ASSIGNMENT_MODELS
from ..models import (
    AccessList,
    ACLExtendedRule,
    ACLInterfaceAssignment,
    ACLStandardRule,
    BaseACLRule,
)
from .nested_serializers import NestedAccessListSerializer

__all__ = [
    "AccessListSerializer",
    "ACLInterfaceAssignmentSerializer",
    "ACLStandardRuleSerializer",
    "ACLExtendedRuleSerializer",
]

# TODO: Check Constants across codebase for consistency.
# Sets a standard error message for ACL rules with an action of remark, but no remark set.
ERROR_MESSAGE_NO_REMARK = "Action is set to remark, you MUST add a remark."
# Sets a standard error message for ACL rules with an action of remark, but no source_prefix is set.
ERROR_MESSAGE_ACTION_REMARK_SOURCE_PREFIX_SET = (
    "Action is set to remark, Source Prefix CANNOT be set."
)
# Sets a standard error message for ACL rules with an action not set to remark, but no remark is set.
ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK = (
    "CANNOT set remark unless action is set to remark."
)
# Sets a standard error message for ACL rules no associated to an ACL of the same type.
ERROR_MESSAGE_ACL_TYPE = "Provided parent Access List is not of right type."


def validate_gfk(data):
    """
    Check that the GFK object is valid.
    """
    # TODO: This can removed after https://github.com/netbox-community/netbox/issues/10221 is fixed.
    try:
        assigned_object = data[  # noqa: F841
            "assigned_object_type"
        ].get_object_for_this_type(
            id=data["assigned_object_id"],
        )
    except ObjectDoesNotExist as e:
        error_message_invalid_gfk = f"Invalid assigned_object {data['assigned_object_type']} ID {data['assigned_object_id']}"
        raise serializers.ValidationError(
            {
                "assigned_object_type": [error_message_invalid_gfk],
                "assigned_object_id": [error_message_invalid_gfk],
            }
        ) from e


class AccessListSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django AccessList model & associates it to a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:accesslist-detail",
    )
    rule_count = serializers.IntegerField(read_only=True)
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(ACL_HOST_ASSIGNMENT_MODELS),
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Associates the django model AccessList & fields to the serializer.
        """

        model = AccessList
        fields = (
            "id",
            "url",
            "display",
            "name",
            "assigned_object_type",
            "assigned_object_id",
            "assigned_object",
            "type",
            "default_action",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "rule_count",
        )

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_assigned_object(self, obj):
        """
        Returns the assigned object for the Access List.
        """
        serializer = get_serializer_for_model(
            obj.assigned_object,
            prefix=NESTED_SERIALIZER_PREFIX,
        )
        context = {"request": self.context["request"]}
        return serializer(obj.assigned_object, context=context).data

    def validate(self, data):
        """
        Validates api inputs before processing:
            - Check that the GFK object is valid.
            - Check if Access List has no existing rules before change the Access List's type.
        """
        error_message = {}

        # Check that the GFK object is valid.
        assigned_object = validate_gfk(data)

        # Check if Access List has no existing rules before change the Access List's type.
        if (
            self.instance
            and self.instance.type != data.get("type")
            and self.instance.rule_count > 0
        ):
            raise serializers.ValidationError(
                {"type": ["This ACL has ACL rules associated, CANNOT change ACL type."]}
            )

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)


class ACLInterfaceAssignmentSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django ACLInterfaceAssignment model & associates it to a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclinterfaceassignment-detail",
    )
    access_list = NestedAccessListSerializer()
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(ACL_INTERFACE_ASSIGNMENT_MODELS),
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Associates the django model ACLInterfaceAssignment & fields to the serializer.
        """

        model = ACLInterfaceAssignment
        fields = (
            "id",
            "url",
            "access_list",
            "direction",
            "assigned_object_type",
            "assigned_object_id",
            "assigned_object",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_assigned_object(self, obj):
        """
        Returns the assigned object for the ACLInterfaceAssignment.
        """
        serializer = get_serializer_for_model(
            obj.assigned_object,
            prefix=NESTED_SERIALIZER_PREFIX,
        )
        context = {"request": self.context["request"]}
        return serializer(obj.assigned_object, context=context).data

    def _validate_get_interface_host(self, data, assigned_object):
        """
        Check that the associated interface's parent host has the selected ACL defined.
        """
        MODEL_MAPPING = {
            "interface": "device",
            "vminterface": "virtual_machine",
        }

        assigned_object_model = data["assigned_object_type"].model

        return getattr(assigned_object, MODEL_MAPPING.get(assigned_object_model, None))

    def _validate_acl_host(self, acl_host, interface_host):
        """
        Check that the associated interface's parent host has the selected ACL defined.
        """
        if acl_host == interface_host:
            return {}

        error_acl_not_assigned_to_host = (
            "Access List not present on the selected interface's host."
        )
        return {
            "access_list": [error_acl_not_assigned_to_host],
            "assigned_object_id": [error_acl_not_assigned_to_host],
        }

    def validate(self, data):
        """
        Validate the AccessList django model's inputs before allowing it to update the instance.
            - Check that the GFK object is valid.
            - Check that the associated interface's parent host has the selected ACL defined.
        """

        # Check that the GFK object is valid.
        assigned_object = validate_gfk(data)

        error_message = {}
        acl_host = data["access_list"].assigned_object

        interface_host = self._validate_get_interface_host(data, assigned_object)
        acl_host = data["access_list"].assigned_object

        error_message |= self._validate_acl_host(acl_host, interface_host)

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)


class BaseACLRuleSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django BaseACLRule model & associates it to a view.
    """

    access_list = NestedAccessListSerializer()
    source_prefix = NestedPrefixSerializer(
        required=False,
        allow_null=True,
        default=None,
    )

    class Meta:
        """
        Associates the django model BaseACLRule & fields to the serializer.
        """

        abstract = True
        model = BaseACLRule
        fields = (
            "id",
            "url",
            "display",
            "access_list",
            "index",
            "action",
            "tags",
            "description",
            "remark",
            "created",
            "custom_fields",
            "last_updated",
            "source_prefix",
        )

    def validate(self, data):
        """
        Validate the BaseACLRule django model's inputs before allowing it to update the instance:
            - Check if action set to remark, but no remark set.
            - Check if action set to remark, but source_prefix set.
        """
        error_message = {}

        # Check if action set to remark, but no remark set.
        if data.get("action") == "remark" and data.get("remark") is None:
            error_message["remark"] = [ERROR_MESSAGE_NO_REMARK]
        # Check if action set to remark, but source_prefix set.
        if data.get("source_prefix"):
            error_message["source_prefix"] = [
                ERROR_MESSAGE_ACTION_REMARK_SOURCE_PREFIX_SET,
            ]

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)


class ACLStandardRuleSerializer(BaseACLRuleSerializer):
    """
    Defines the serializer for the django ACLStandardRule model & associates it to a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclstandardrule-detail",
    )

    class Meta(BaseACLRuleSerializer.Meta):
        """
        Associates the django model ACLStandardRule & fields to the serializer.
        """

        model = ACLStandardRule


class ACLExtendedRuleSerializer(BaseACLRuleSerializer):
    """
    Defines the serializer for the django ACLExtendedRule model & associates it to a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclextendedrule-detail",
    )
    destination_prefix = NestedPrefixSerializer(
        required=False,
        allow_null=True,
        default=None,
    )

    class Meta(BaseACLRuleSerializer.Meta):
        """
        Associates the django model ACLExtendedRule & fields to the serializer.
        """

        model = ACLExtendedRule

        # Add the additional fields to the serializer to support Extended ACL Rules.
        fields = BaseACLRuleSerializer.Meta.fields + (
            "source_ports",
            "destination_prefix",
            "destination_ports",
            "protocol",
            "remark",
        )

    def validate(self, data):
        """
        Validate the ACLExtendedRule django model's inputs before allowing it to update the instance:
            - Check if action set to remark, but no remark set.
            - Check if action set to remark, but source_prefix set.
            - Check if action set to remark, but source_ports set.
            - Check if action set to remark, but destination_prefix set.
            - Check if action set to remark, but destination_ports set.
            - Check if action set to remark, but protocol set.
            - Check if action set to remark, but protocol set.
        """
        error_message = {}
        rule_attributes = [
            "source_prefix",
            "source_ports",
            "destination_prefix",
            "destination_ports",
            "protocol",
        ]

        # Check if action set to remark, but no remark set.
        if data.get("action") == "remark" and data.get("remark") is None:
            error_message["remark"] = [ERROR_MESSAGE_NO_REMARK]

        # Check if action set to remark, but other fields set.
        for attribute in rule_attributes:
            if data.get(attribute):
                error_message[attribute] = [
                    f'Action is set to remark, {attribute.replace("_", " ").title()} CANNOT be set.'
                ]

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)
