"""
Serializers control the translation of client data to and from Python objects,
while Django itself handles the database abstraction.
"""

from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from netbox.api.fields import ContentTypeField, IntegerRangeSerializer
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer, PrimaryModelSerializer
from users.api.serializers_.mixins import OwnerMixin

from ..constants import ACL_ASSIGNMENT_MODELS, ACL_RULE_SOURCE_DESTINATION_MODELS
from ..models import (
    AccessList,
    ACLAssignment,
    ACLExtendedRule,
    ACLStandardRule,
)
from ..utils import normalize_log_options

__all__ = [
    "ACLAssignmentSerializer",
    "ACLExtendedRuleSerializer",
    "ACLStandardRuleSerializer",
    "AccessListSerializer",
]

#
# Access Lists
#


class AccessListSerializer(PrimaryModelSerializer):
    """
    Defines the serializer for the django AccessList model and associates it with a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:accesslist-detail",
    )
    rule_count = serializers.IntegerField(read_only=True)

    class Meta:
        """
        Associates the django model AccessList & fields with the serializer.
        """

        model = AccessList
        fields = (
            "id",
            "url",
            "display",
            "name",
            "type",
            "family",
            "default_action",
            "description",
            "owner",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "rule_count",
        )
        brief_fields = ("id", "url", "display", "name")


#
# ACL Assignments
#


class ACLAssignmentSerializer(OwnerMixin, NetBoxModelSerializer):
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
    assigned_object = GFKSerializerField(read_only=True)

    # Denormalized fields
    family = serializers.CharField(read_only=True)

    class Meta:
        """
        Associates the django model ACLAssignment & fields with the serializer.
        """

        model = ACLAssignment
        fields = (
            "id",
            "url",
            "display",
            "access_list",
            "family",
            "direction",
            "assigned_object_type",
            "assigned_object_id",
            "assigned_object",
            "owner",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "access_list")


#
# Access List Rules
#


class ACLRuleSerializerMixin(serializers.Serializer):
    """
    Fields and brief fields shared by both concrete rule serializers.

    Validation belongs to the models, which full_clean() reaches through
    ValidatedModelSerializer.
    """

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
    source = GFKSerializerField(read_only=True)

    class Meta:
        brief_fields = (
            "id",
            "url",
            "display",
            "access_list",
            "sequence",
        )

    def validate_log_options(self, value):
        """
        Store log options canonically.
        """
        # ValidatedModelSerializer does not copy the cleaned instance back, so the model's
        # normalization never reaches validated_data.
        return normalize_log_options(value)


class ACLStandardRuleSerializer(ACLRuleSerializerMixin, PrimaryModelSerializer):
    """
    Defines the serializer for the django ACLStandardRule model and associates it with a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclstandardrule-detail",
    )

    class Meta(ACLRuleSerializerMixin.Meta):
        """
        Associates the django model ACLStandardRule & fields with the serializer.
        """

        model = ACLStandardRule
        fields = (
            "id",
            "url",
            "display",
            "access_list",
            "sequence",
            "action",
            "remark",
            "source_type",
            "source_id",
            "source",
            "log_matches",
            "log_options",
            "description",
            "owner",
            "comments",
            "tags",
            "created",
            "custom_fields",
            "last_updated",
        )


class ACLExtendedRuleSerializer(ACLRuleSerializerMixin, PrimaryModelSerializer):
    """
    Defines the serializer for the django ACLExtendedRule model and associates it with a view.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_acls-api:aclextendedrule-detail",
    )
    source_port_ranges = IntegerRangeSerializer(many=True, required=False)
    source_port_terms = serializers.SerializerMethodField(read_only=True)
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
    destination = GFKSerializerField(read_only=True)
    destination_port_ranges = IntegerRangeSerializer(many=True, required=False)
    destination_port_terms = serializers.SerializerMethodField(read_only=True)

    class Meta(ACLRuleSerializerMixin.Meta):
        """
        Associates the django model ACLExtendedRule & fields to the serializer.
        """

        model = ACLExtendedRule
        fields = (
            "id",
            "url",
            "display",
            "access_list",
            "sequence",
            "action",
            "remark",
            "protocol",
            "source_type",
            "source_id",
            "source",
            "source_port_ranges",
            "source_port_terms",
            "destination_type",
            "destination_id",
            "destination",
            "destination_port_ranges",
            "destination_port_terms",
            "log_matches",
            "log_options",
            "description",
            "owner",
            "comments",
            "tags",
            "created",
            "custom_fields",
            "last_updated",
        )

    @extend_schema_field({"type": "array", "items": {"type": "string"}})
    def get_destination_port_terms(self, obj):
        """
        Fetches the destination port terms for the given object.
        """
        return obj.destination_port_ranges_list

    @extend_schema_field({"type": "array", "items": {"type": "string"}})
    def get_source_port_terms(self, obj):
        """
        Fetches the source port terms for the given object.
        """
        return obj.source_port_ranges_list
