"""
Serializers control the translation of client data to and from Python objects,
while Django itself handles the database abstraction.
"""

from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from utilities.api import get_serializer_for_model

from ..constants import ACL_ASSIGNMENT_MODELS, ACL_RULE_SOURCE_DESTINATION_MODELS
from ..models import (
    AccessList,
    ACLExtendedRule,
    ACLAssignment,
    ACLStandardRule,
)

__all__ = [
    "AccessListSerializer",
    "ACLAssignmentSerializer",
    "ACLStandardRuleSerializer",
    "ACLExtendedRuleSerializer",
]

# Sets a standard error message for ACL rules with an action of remark, but no remark set.
error_message_no_remark = "Action is set to remark, you MUST add a remark."
# Sets a standard error message for ACL rules with an action of remark, but no source is set.
error_message_action_remark_source_set = "Action is set to remark, Source CANNOT be set."
# Sets a standard error message for ACL rules with an action not set to remark, but no remark is set.
error_message_remark_without_action_remark = "CANNOT set remark unless action is set to remark."
# Sets a standard error message for ACL rules no associated with an ACL of the same type.
error_message_acl_type = "Provided parent Access List is not of right type."


class AccessListSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django AccessList model and associates it with a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:accesslist-detail",
    )
    rule_count = serializers.IntegerField(read_only=True)

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
            "type",
            "default_action",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "rule_count",
        )
        brief_fields = ("id", "url", "display", "name")

    def validate(self, data):
        """
        Validates api inputs before processing:
          - Check that the GFK object is valid.
          - Check if Access List has no existing rules before change the Access List's type.
        """
        error_message = {}

        # Check if Access List has no existing rules before change the Access List's type.
        if self.instance and self.instance.type != data.get("type") and self.instance.rule_count > 0:
            error_message["type"] = [
                "This ACL has ACL rules associated, CANNOT change ACL type.",
            ]

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)


class ACLAssignmentSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django ACLAssignment model and associates it with a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclassignment-detail",
    )
    access_list = AccessListSerializer(nested=True, required=True)
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(ACL_ASSIGNMENT_MODELS),
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Associates the django model ACLAssignment & fields to the serializer.
        """

        model = ACLAssignment
        fields = (
            "id",
            "url",
            "display",
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
        brief_fields = ("id", "url", "display", "access_list")

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_assigned_object(self, obj):
        if obj.assigned_object is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_object)
        context = {"request": self.context["request"]}
        return serializer(obj.assigned_object, nested=True, context=context).data


class ACLStandardRuleSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django ACLStandardRule model and associates it with a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclstandardrule-detail",
    )
    access_list = AccessListSerializer(nested=True, required=True)
    source_type = ContentTypeField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        default=None,
        allow_null=True,
    )
    source_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    source = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Associates the django model ACLStandardRule & fields to the serializer.
        """

        model = ACLStandardRule
        fields = (
            "id",
            "url",
            "display",
            "access_list",
            "index",
            "action",
            "remark",
            "source_type",
            "source_id",
            "source",
            "description",
            "tags",
            "created",
            "custom_fields",
            "last_updated",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "access_list",
            "index",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_source(self, obj):
        if obj.source_id is None:
            return None
        serializer = get_serializer_for_model(obj.source)
        context = {"request": self.context["request"]}
        return serializer(obj.source, nested=True, context=context).data

    def validate(self, data):
        """
        Validate the ACLStandardRule django model's inputs before allowing it to update the instance:
          - Check if action set to remark, but no remark set.
          - Check if action set to remark, but source set.
        """
        error_message = {}

        if data.get("action") == "remark":
            # Check if action set to remark, but no remark set.
            if data.get("remark") is None:
                error_message["remark"] = [
                    error_message_no_remark,
                ]
            # Check if action set to remark, but the source set.
            if data.get("source"):
                error_message["source"] = [
                    error_message_action_remark_source_set,
                ]

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)


class ACLExtendedRuleSerializer(NetBoxModelSerializer):
    """
    Defines the serializer for the django ACLExtendedRule model and associates it with a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclextendedrule-detail",
    )
    access_list = AccessListSerializer(nested=True, required=True)
    source_type = ContentTypeField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        default=None,
        allow_null=True,
    )
    source_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    source = serializers.SerializerMethodField(read_only=True)
    destination_type = ContentTypeField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        default=None,
        allow_null=True,
    )
    destination_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    destination = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Associates the django model ACLExtendedRule & fields to the serializer.
        """

        model = ACLExtendedRule
        fields = (
            "id",
            "url",
            "display",
            "access_list",
            "index",
            "action",
            "remark",
            "protocol",
            "source_type",
            "source_id",
            "source",
            "source_ports",
            "destination_type",
            "destination_id",
            "destination",
            "destination_ports",
            "description",
            "tags",
            "created",
            "custom_fields",
            "last_updated",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "access_list",
            "index",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_source(self, obj):
        if obj.source_id is None:
            return None
        serializer = get_serializer_for_model(obj.source)
        context = {"request": self.context["request"]}
        return serializer(obj.source, nested=True, context=context).data

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_destination(self, obj):
        if obj.destination_id is None:
            return None
        serializer = get_serializer_for_model(obj.destination)
        context = {"request": self.context["request"]}
        return serializer(obj.destination, nested=True, context=context).data

    def validate(self, data):
        """
        Validate the ACLExtendedRule django model's inputs before allowing it to update the instance:
          - Check if action set to remark, but no remark set.
          - Check if action set to remark, but source set.
          - Check if action set to remark, but source_ports set.
          - Check if action set to remark, but destination set.
          - Check if action set to remark, but destination_ports set.
          - Check if action set to remark, but protocol set.
          - Check if action set to remark, but protocol set.
        """
        error_message = {}

        if data.get("action") == "remark":
            # Check if action set to remark, but no remark set.
            if data.get("remark") is None:
                error_message["remark"] = [
                    error_message_no_remark,
                ]
            # Check if action set to remark, but the source set.
            if data.get("source"):
                error_message["source"] = [
                    error_message_action_remark_source_set,
                ]
            # Check if action set to remark, but source_ports set.
            if data.get("source_ports"):
                error_message["source_ports"] = [
                    "Action is set to remark, Source Ports CANNOT be set.",
                ]
            # Check if action set to remark, but destination set.
            if data.get("destination"):
                error_message["destination"] = [
                    "Action is set to remark, Destination Prefix CANNOT be set.",
                ]
            # Check if action set to remark, but destination_ports set.
            if data.get("destination_ports"):
                error_message["destination_ports"] = [
                    "Action is set to remark, Destination Ports CANNOT be set.",
                ]
            # Check if action set to remark, but protocol set.
            if data.get("protocol"):
                error_message["protocol"] = [
                    "Action is set to remark, Protocol CANNOT be set.",
                ]

        if error_message:
            raise serializers.ValidationError(error_message)

        return super().validate(data)
