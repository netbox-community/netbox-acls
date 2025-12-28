"""
Define the django models for this plugin.
"""

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.models import NetBoxModel

from ..choices import ACLProtocolChoices, ACLRuleActionChoices, ACLTypeChoices
from ..constants import ACL_RULE_SOURCE_DESTINATION_MODELS
from .access_lists import AccessList

__all__ = (
    "ACLRule",
    "ACLStandardRule",
    "ACLExtendedRule",
)

# Error message when the action is 'remark', but no remark is provided.
ERROR_MESSAGE_NO_REMARK = _("When the action is 'remark', a remark is required.")

# Error message when the action is 'remark', but the source is set.
ERROR_MESSAGE_ACTION_REMARK_SOURCE_SET = _("When the action is 'remark', the Source must not be set.")

# Error message when the action is 'remark', but the source_ports are set.
ERROR_MESSAGE_ACTION_REMARK_SOURCE_PORTS_SET = _("When the action is 'remark', Source Ports must not be set.")

# Error message when the action is 'remark', but the destination is set.
ERROR_MESSAGE_ACTION_REMARK_DESTINATION_SET = _("When the action is 'remark', the Destination must not be set.")

# Error message when the action is 'remark', but the destination_ports are set.
ERROR_MESSAGE_ACTION_REMARK_DESTINATION_PORTS_SET = _("When the action is 'remark', Destination Ports must not be set.")

# Error message when the action is 'remark', but the protocol is set.
ERROR_MESSAGE_ACTION_REMARK_PROTOCOL_SET = _("When the action is 'remark', Protocol must not be set.")

# Error message when a remark is provided, but the action is not set to 'remark'.
ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK = _("A remark cannot be set unless the action is 'remark'.")


class ACLRule(NetBoxModel):
    """
    Abstract model for ACL Rules.
    Inherited by both ACLStandardRule and ACLExtendedRule.
    """

    access_list = models.ForeignKey(
        to=AccessList,
        on_delete=models.CASCADE,
        related_name="rules",
        verbose_name=_("Access List"),
    )

    # Rule
    index = models.PositiveIntegerField()
    description = models.CharField(
        verbose_name=_("Description"),
        max_length=500,
        blank=True,
    )
    action = models.CharField(
        verbose_name=_("Action"),
        max_length=30,
        choices=ACLRuleActionChoices,
    )

    # Remark
    remark = models.CharField(
        verbose_name=_("Remark"),
        max_length=500,
        blank=True,
    )

    # Source
    source_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=ACL_RULE_SOURCE_DESTINATION_MODELS,
        verbose_name=_("Source Type"),
        blank=True,
        null=True,
    )
    source_id = models.PositiveBigIntegerField(
        verbose_name=_("Source ID"),
        blank=True,
        null=True,
    )
    source = GenericForeignKey(
        ct_field="source_type",
        fk_field="source_id",
    )

    # Cached related objects by association name for faster access
    _source_aggregate = models.ForeignKey(
        to="ipam.aggregate",
        on_delete=models.PROTECT,
        related_name="_%(class)s_sources",
        verbose_name=_("Source Aggregate"),
        blank=True,
        null=True,
    )
    _source_ipaddress = models.ForeignKey(
        to="ipam.ipaddress",
        on_delete=models.PROTECT,
        related_name="_%(class)s_sources",
        verbose_name=_("Source IP-Address"),
        blank=True,
        null=True,
    )
    _source_iprange = models.ForeignKey(
        to="ipam.iprange",
        on_delete=models.PROTECT,
        related_name="_%(class)s_sources",
        verbose_name=_("Source IP-Range"),
        blank=True,
        null=True,
    )
    _source_prefix = models.ForeignKey(
        to="ipam.prefix",
        on_delete=models.PROTECT,
        related_name="_%(class)s_sources",
        verbose_name=_("Source Prefix"),
        blank=True,
        null=True,
    )

    clone_fields = (
        "access_list",
        "action",
        "source_id",
        "source_type",
    )
    prerequisite_models: tuple = ("netbox_acls.AccessList",)

    class Meta:
        """
        Define the common model properties:
          - as an abstract model
          - ordering
          - unique together
        """

        abstract = True
        indexes = (models.Index(fields=("source_type", "source_id")),)
        ordering = ["access_list", "index"]
        unique_together = ["access_list", "index"]

    def __str__(self):
        return f"{self.access_list}: Rule {self.index}"

    def clean(self):
        """
        Override the model's clean method for custom field validation.
        """
        # Validate source assignment
        if self.source_type and not (self.source or self.source_id):
            source_type = self.source_type.model_class()
            raise ValidationError(
                {
                    "source": _("Please select a source {source_type}.").format(
                        source_type=source_type._meta.verbose_name
                    )
                }
            )
        super().clean()

    def save(self, *args, **kwargs):
        """
        Saves the current instance to the database.
        """
        # Cache the related source objects for faster access
        self.cache_related_source_object()

        super().save(*args, **kwargs)

    def cache_related_source_object(self):
        """
        Cache the related source objects for faster access.
        """
        self._source_aggregate = self._source_ipaddress = self._source_iprange = self._source_prefix = None
        if self.source_type:
            source_type = self.source_type.model_class()
            if source_type == apps.get_model("ipam", "aggregate"):
                self._source_aggregate = self.source
            elif source_type == apps.get_model("ipam", "ipaddress"):
                self._source_ipaddress = self.source
            elif source_type == apps.get_model("ipam", "iprange"):
                self._source_iprange = self.source
            elif source_type == apps.get_model("ipam", "prefix"):
                self._source_prefix = self.source

    cache_related_source_object.alters_data = True

    def get_action_color(self):
        return ACLRuleActionChoices.colors.get(self.action)


class ACLStandardRule(ACLRule):
    """
    Inherits ACLRule.
    """

    access_list = models.ForeignKey(
        to=AccessList,
        on_delete=models.CASCADE,
        related_name="aclstandardrules",
        limit_choices_to={"type": ACLTypeChoices.TYPE_STANDARD},
        verbose_name=_("Standard Access List"),
    )

    class Meta(ACLRule.Meta):
        """
        Define the model properties adding to or overriding the inherited class:
          - default_related_name for any FK relationships
          - verbose name (for displaying in the GUI)
          - verbose name plural (for displaying in the GUI)
        """

        verbose_name = _("ACL Standard Rule")
        verbose_name_plural = _("ACL Standard Rules")

    def clean(self):
        """
        Validate the ACL Standard Rule inputs.

        If the action is 'remark', then the remark field must be provided (non-empty),
        and the source field must be empty.
        Conversely, if the remark field is provided, the action must be set to 'remark'.
        """

        super().clean()
        errors = {}

        # Validate that only the remark field is filled
        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if not self.remark:
                errors["remark"] = ERROR_MESSAGE_NO_REMARK
            if self.source:
                errors["source"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_SET
        # Validate that the action is "remark", when the remark field is provided
        elif self.remark:
            errors["remark"] = ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK

        if errors:
            raise ValidationError(errors)


class ACLExtendedRule(ACLRule):
    """
    Inherits ACLRule.

    Add ACLExtendedRule specific fields: source_ports, destination, destination_ports, and protocol
    """

    access_list = models.ForeignKey(
        to=AccessList,
        on_delete=models.CASCADE,
        related_name="aclextendedrules",
        limit_choices_to={"type": "extended"},
        verbose_name=_("Extended Access List"),
    )

    # Protocol
    protocol = models.CharField(
        verbose_name=_("Protocol"),
        max_length=30,
        choices=ACLProtocolChoices,
        blank=True,
    )

    # Source
    source_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        verbose_name=_("Source Ports"),
        blank=True,
        null=True,
    )

    # Destination
    destination_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=ACL_RULE_SOURCE_DESTINATION_MODELS,
        verbose_name=_("Destination Type"),
        blank=True,
        null=True,
    )
    destination_id = models.PositiveBigIntegerField(
        verbose_name=_("Destination ID"),
        blank=True,
        null=True,
    )
    destination = GenericForeignKey(
        ct_field="destination_type",
        fk_field="destination_id",
    )
    destination_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        verbose_name=_("Destination Ports"),
        blank=True,
        null=True,
    )

    # Cached related objects by association name for faster access
    _destination_aggregate = models.ForeignKey(
        to="ipam.aggregate",
        on_delete=models.PROTECT,
        related_name="_%(class)s_destinations",
        verbose_name=_("Destination Aggregate"),
        blank=True,
        null=True,
    )
    _destination_ipaddress = models.ForeignKey(
        to="ipam.ipaddress",
        on_delete=models.PROTECT,
        related_name="_%(class)s_destinations",
        verbose_name=_("Destination IP-Address"),
        blank=True,
        null=True,
    )
    _destination_iprange = models.ForeignKey(
        to="ipam.iprange",
        on_delete=models.PROTECT,
        related_name="_%(class)s_destinations",
        verbose_name=_("Destination IP-Range"),
        blank=True,
        null=True,
    )
    _destination_prefix = models.ForeignKey(
        to="ipam.prefix",
        on_delete=models.PROTECT,
        related_name="_%(class)s_destinations",
        verbose_name=_("Destination Prefix"),
        blank=True,
        null=True,
    )

    clone_fields = (
        "access_list",
        "action",
        "source_id",
        "source_type",
        "source_ports",
        "destination_id",
        "destination_type",
        "destination_ports",
        "protocol",
    )

    class Meta(ACLRule.Meta):
        """
        Define the model properties adding to or overriding the inherited class:
          - default_related_name for any FK relationships
          - verbose name (for displaying in the GUI)
          - verbose name plural (for displaying in the GUI)
        """

        verbose_name = _("ACL Extended Rule")
        verbose_name_plural = _("ACL Extended Rules")
        indexes = (models.Index(fields=("destination_type", "destination_id", "source_type", "source_id")),)

    def clean(self):
        """
        Validate the ACL Extended Rule inputs.

        When the action is 'remark', the remark field must be provided (non-empty),
        and the following fields must be empty:
          - source
          - source_ports
          - destination
          - destination_ports
          - protocol

        Conversely, if a remark is provided, the action must be set to 'remark'.
        """
        # Validate destination assignment
        if self.destination_type and not (self.destination or self.destination_id):
            destination_type = self.destination_type.model_class()
            raise ValidationError(
                {
                    "destination": _("Please select a destination {destination_type}.").format(
                        destination_type=destination_type._meta.verbose_name,
                    ),
                },
            )

        super().clean()

        errors = {}

        # Validate that only the remark field is filled
        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if not self.remark:
                errors["remark"] = ERROR_MESSAGE_NO_REMARK
            if self.source:
                errors["source"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_SET
            if self.source_ports:
                errors["source_ports"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_PORTS_SET
            if self.destination:
                errors["destination"] = ERROR_MESSAGE_ACTION_REMARK_DESTINATION_SET
            if self.destination_ports:
                errors["destination_ports"] = ERROR_MESSAGE_ACTION_REMARK_DESTINATION_PORTS_SET
            if self.protocol:
                errors["protocol"] = ERROR_MESSAGE_ACTION_REMARK_PROTOCOL_SET
        # Validate that the action is "remark", when the remark field is provided
        elif self.remark:
            errors["remark"] = ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Saves the current instance to the database.
        """
        # Cache the related destination objects for faster access
        self.cache_related_destination_objects()

        super().save(*args, **kwargs)

    def cache_related_destination_objects(self):
        """
        Cache the related destination objects for faster access.
        """
        self._destination_aggregate = self._destination_ipaddress = self._destination_iprange = (
            self._destination_prefix
        ) = None
        if self.destination_type:
            destination_type = self.destination_type.model_class()
            if destination_type == apps.get_model("ipam", "aggregate"):
                self._destination_aggregate = self.destination
            elif destination_type == apps.get_model("ipam", "ipaddress"):
                self._destination_ipaddress = self.destination
            elif destination_type == apps.get_model("ipam", "iprange"):
                self._destination_iprange = self.destination
            elif destination_type == apps.get_model("ipam", "prefix"):
                self._destination_prefix = self.destination

    cache_related_destination_objects.alters_data = True

    def get_protocol_color(self):
        return ACLProtocolChoices.colors.get(self.protocol)


#
# Generic Relations: ACLStandardRule
#

# Source Aggregate
GenericRelation(
    to=ACLStandardRule,
    content_type_field="source_type",
    object_id_field="source_id",
    related_query_name="source_aggregate",
).contribute_to_class(Aggregate, "accesslist_standard_rule_sources")

# Source IPAddress
GenericRelation(
    to=ACLStandardRule,
    content_type_field="source_type",
    object_id_field="source_id",
    related_query_name="source_ip_address",
).contribute_to_class(IPAddress, "accesslist_standard_rule_sources")

# Source IPRange
GenericRelation(
    to=ACLStandardRule,
    content_type_field="source_type",
    object_id_field="source_id",
    related_query_name="source_ip_range",
).contribute_to_class(IPRange, "accesslist_standard_rule_sources")

# Source Prefix
GenericRelation(
    to=ACLStandardRule,
    content_type_field="source_type",
    object_id_field="source_id",
    related_query_name="source_prefix",
).contribute_to_class(Prefix, "accesslist_standard_rule_sources")


#
# Generic Relations: ACLExtendedRule
#

# Source Aggregate
GenericRelation(
    to=ACLExtendedRule,
    content_type_field="source_type",
    object_id_field="source_id",
    related_query_name="source_aggregate",
).contribute_to_class(Aggregate, "accesslist_extended_rule_sources")

# Source IPAddress
GenericRelation(
    to=ACLExtendedRule,
    content_type_field="source_type",
    object_id_field="source_id",
    related_query_name="source_ip_address",
).contribute_to_class(IPAddress, "accesslist_extended_rule_sources")

# Source IPRange
GenericRelation(
    to=ACLExtendedRule,
    content_type_field="source_type",
    object_id_field="source_id",
    related_query_name="source_ip_range",
).contribute_to_class(IPRange, "accesslist_extended_rule_sources")

# Source Prefix
GenericRelation(
    to=ACLExtendedRule,
    content_type_field="source_type",
    object_id_field="source_id",
    related_query_name="source_prefix",
).contribute_to_class(Prefix, "accesslist_extended_rule_sources")

# Destination Aggregate
GenericRelation(
    to=ACLExtendedRule,
    content_type_field="destination_type",
    object_id_field="destination_id",
    related_query_name="destination_aggregate",
).contribute_to_class(Aggregate, "accesslist_extended_rule_destinations")

# Destination IPAddress
GenericRelation(
    to=ACLExtendedRule,
    content_type_field="destination_type",
    object_id_field="destination_id",
    related_query_name="destination_ip_address",
).contribute_to_class(IPAddress, "accesslist_extended_rule_destinations")

# Destination IPRange
GenericRelation(
    to=ACLExtendedRule,
    content_type_field="destination_type",
    object_id_field="destination_id",
    related_query_name="destination_ip_range",
).contribute_to_class(IPRange, "accesslist_extended_rule_destinations")

# Destination Prefix
GenericRelation(
    to=ACLExtendedRule,
    content_type_field="destination_type",
    object_id_field="destination_id",
    related_query_name="destination_prefix",
).contribute_to_class(Prefix, "accesslist_extended_rule_destinations")
