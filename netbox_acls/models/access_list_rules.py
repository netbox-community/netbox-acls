"""
Define the django models for this plugin.
"""

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import ArrayField, IntegerRangeField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.models import PrimaryModel
from utilities.data import ranges_to_string_list
from utilities.object_types import object_type_identifier

from ..choices import (
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ..constants import ACL_RULE_SOURCE_DESTINATION_MODELS
from ..utils import infer_family_from_object, normalize_log_options, normalize_port_ranges
from ..validators import validate_port_ranges
from .access_lists import AccessList
from .managers import ACLRuleManager

__all__ = (
    "ACLExtendedRule",
    "ACLRule",
    "ACLStandardRule",
)

# Error message when the action is 'remark', but no remark is provided.
ERROR_MESSAGE_NO_REMARK = _("When the action is 'remark', a remark is required.")

# Error message when the action is 'remark', but the source is set.
ERROR_MESSAGE_ACTION_REMARK_SOURCE_SET = _("When the action is 'remark', the Source must not be set.")

# Error message when the action is 'remark', but the source_port_ranges are set.
ERROR_MESSAGE_ACTION_REMARK_SOURCE_PORTS_SET = _("When the action is 'remark', Source Ports must not be set.")

# Error message when the action is 'remark', but the destination is set.
ERROR_MESSAGE_ACTION_REMARK_DESTINATION_SET = _("When the action is 'remark', the Destination must not be set.")

# Error message when the action is 'remark', but the destination_port_ranges are set.
ERROR_MESSAGE_ACTION_REMARK_DESTINATION_PORTS_SET = _("When the action is 'remark', Destination Ports must not be set.")

# Error message when the action is 'remark', but the protocol is set.
ERROR_MESSAGE_ACTION_REMARK_PROTOCOL_SET = _("When the action is 'remark', Protocol must not be set.")

# Error message when log options are set but logging is disabled.
ERROR_MESSAGE_LOG_OPTIONS_WITHOUT_LOG_MATCHES = _("Log options require Log matches to be enabled.")

# Error message when the action is 'remark', but logging is enabled.
ERROR_MESSAGE_ACTION_REMARK_LOG_MATCHES_SET = _("When the action is 'remark', Log matches must not be enabled.")

# Error message when the action is 'remark', but log options are set.
ERROR_MESSAGE_ACTION_REMARK_LOG_OPTIONS_SET = _("When the action is 'remark', Log options must not be set.")

# Error message when the protocol is not 'TCP' or 'UDP', but the source ports are set.
ERROR_MESSAGE_PROTOCOL_NOT_TCP_OR_UDP_WITH_SOURCE_PORTS_SET = _(
    "Source Ports can only be set when the protocol is TCP or UDP."
)

# Error message when the protocol is not 'TCP' or 'UDP', but the destination ports are set.
ERROR_MESSAGE_PROTOCOL_NOT_TCP_OR_UDP_WITH_DESTINATION_PORTS_SET = _(
    "Destination Ports can only be set when the protocol is TCP or UDP."
)

# Help text for the log options field, shared by the model and both form modules.
HELP_TEXT_ACL_RULE_LOG_OPTIONS = _(
    "Optional logging attributes. Leave empty for the target platform's default. "
    "Vendor-specific options are grouped by vendor and are platform-dependent."
)


class ACLRule(PrimaryModel):
    """
    Abstract model for ACL Rules.
    Inherited by both ACLStandardRule and ACLExtendedRule.
    """

    access_list = models.ForeignKey(
        to=AccessList,
        on_delete=models.CASCADE,
        verbose_name=_("Access List"),
    )

    # Rule
    sequence = models.PositiveIntegerField()
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

    # Logging
    log_matches = models.BooleanField(
        verbose_name=_("Log matches"),
        default=False,
        help_text=_("Request logging for packets matching this rule."),
    )
    log_options = ArrayField(
        base_field=models.CharField(
            max_length=100,
            choices=ACLRuleLogOptionChoices,
        ),
        verbose_name=_("Log options"),
        default=list,
        blank=True,
        help_text=HELP_TEXT_ACL_RULE_LOG_OPTIONS,
    )

    objects = ACLRuleManager()

    clone_fields = (
        "access_list",
        "action",
        "source_id",
        "source_type",
        "log_matches",
        "log_options",
    )
    prerequisite_models: tuple = ("netbox_acls.AccessList",)

    # Generic references mirrored into shadow columns, one set per role.
    cached_object_roles = ("source",)

    class Meta:
        """
        Define the common model properties:
          - as an abstract model
          - constraints (unique together)
          - sequence
          - ordering
        """

        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=("access_list", "sequence"),
                name="%(app_label)s_%(class)s_unique_aclrule_sequence",
                violation_error_message=_("Unique ACL rule sequence already exists."),
            ),
        ]
        indexes = (models.Index(fields=("source_type", "source_id")),)
        ordering = ("access_list", "sequence", "-action")

    def __str__(self):
        """
        Returns a string representation of the object.

        This method generates a human-readable representation for the object
        by including its access list and rule sequence.
        """
        return f"{self.access_list}: Rule {self.sequence}"

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

        # Validate rule family
        self._validate_rule_family()

    def clone(self):
        """
        Creates a clone of the current ACL rule instance.
        """
        attrs = super().clone()

        # Use the next sequence for clone / create-and-add-another
        if self.access_list_id:
            attrs["sequence"] = self.__class__.objects.get_next_sequence(self.access_list_id)

        return attrs

    def save(self, *args, **kwargs):
        """
        Saves the current instance to the database.
        """
        # Cache the related objects for faster access
        for role in self.cached_object_roles:
            self.cache_related_objects(role)

        super().save(*args, **kwargs)

    def cache_related_objects(self, role):
        """
        Refresh one role's shadow columns from its generic reference.
        """
        content_type = getattr(self, f"{role}_type")
        label = object_type_identifier(content_type) if content_type else None
        prefix = f"_{role}_"

        # Shadow columns are located by name, so _<role>_<model> is a contract.
        for field in self._meta.fields:
            if not field.is_relation or not field.name.startswith(prefix):
                continue
            matched = field.related_model._meta.label_lower == label
            setattr(self, field.name, getattr(self, role) if matched else None)

    cache_related_objects.alters_data = True

    def _validate_rule_family(self):
        """
        Validates that the ACL rule's family matches the source and destination families.
        """
        acl_family = self.access_list.family
        families = set()

        # Source
        source = getattr(self, "source", None)
        if source:
            fam = infer_family_from_object(source)
            if fam:
                families.add(fam)

        # Destination (extended only)
        destination = getattr(self, "destination", None)
        if destination:
            fam = infer_family_from_object(destination)
            if fam:
                families.add(fam)

        # Enforce
        if acl_family == ACLFamilyChoices.FAMILY_IPV4 and ACLFamilyChoices.FAMILY_IPV6 in families:
            raise ValidationError(_("IPv4 ACL: Rule contains IPv6 criteria."))
        if acl_family == ACLFamilyChoices.FAMILY_IPV6 and ACLFamilyChoices.FAMILY_IPV4 in families:
            raise ValidationError(_("IPv6 ACL: Rule contains IPv4 criteria."))
        if acl_family == ACLFamilyChoices.FAMILY_DUAL and len(families) > 1:
            raise ValidationError(_("Dual-stack ACL: A single rule must not mix IPv4 and IPv6 criteria."))

    def get_action_color(self):
        """
        Returns the color associated with the action of an ACL rule.
        """
        return ACLRuleActionChoices.colors.get(self.action)

    def to_objectchange(self, action):
        """
        Creates an ObjectChange instance for the ACL rule.
        """
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.access_list
        return objectchange

    @property
    def log_options_badges(self) -> list[tuple[str, str | None]]:
        """
        Return the display label and badge color of each stored log option.
        """
        labels = dict(self._meta.get_field("log_options").base_field.flatchoices)
        colors = ACLRuleLogOptionChoices.colors
        return [(str(labels.get(value, value)), colors.get(value)) for value in self.log_options]

    @property
    def log_options_list(self) -> list[str]:
        """
        Return the display labels, passing through values no longer configured.
        """
        return [label for label, _color in self.log_options_badges]

    def _validate_logging(self):
        """
        Return field errors for an inconsistent logging state.
        """
        errors = {}

        if not self.log_matches and self.log_options:
            errors["log_options"] = ERROR_MESSAGE_LOG_OPTIONS_WITHOUT_LOG_MATCHES

        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if self.log_matches:
                errors["log_matches"] = ERROR_MESSAGE_ACTION_REMARK_LOG_MATCHES_SET
            if self.log_options:
                errors["log_options"] = ERROR_MESSAGE_ACTION_REMARK_LOG_OPTIONS_SET

        return errors


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

        self.log_options = normalize_log_options(self.log_options or [])
        errors.update(self._validate_logging())

        # Validate that only the remark field is filled
        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if not self.remark:
                errors["remark"] = ERROR_MESSAGE_NO_REMARK
            if self.source:
                errors["source"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_SET

        if errors:
            raise ValidationError(errors)


class ACLExtendedRule(ACLRule):
    """
    Inherits ACLRule.

    Add ACLExtendedRule specific fields: source_port_ranges, destination, destination_port_ranges, and protocol
    """

    access_list = models.ForeignKey(
        to=AccessList,
        on_delete=models.CASCADE,
        related_name="aclextendedrules",
        limit_choices_to={"type": ACLTypeChoices.TYPE_EXTENDED},
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
    source_port_ranges = ArrayField(
        base_field=IntegerRangeField(),
        verbose_name=_("Source Port Ranges"),
        default=list,
        blank=True,
        help_text=_("Inclusive port ranges (e.g., 10-20,22,80-81)."),
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
    destination_port_ranges = ArrayField(
        base_field=IntegerRangeField(),
        verbose_name=_("Destination Port Ranges"),
        default=list,
        blank=True,
        help_text=_("Inclusive port ranges (e.g., 10-20,22,80-81)."),
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

    clone_fields = ACLRule.clone_fields + (
        "source_port_ranges",
        "destination_id",
        "destination_type",
        "destination_port_ranges",
        "protocol",
    )

    cached_object_roles = ("source", "destination")

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
          - source_port_ranges
          - destination
          - destination_port_ranges
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

        self.log_options = normalize_log_options(self.log_options or [])
        errors.update(self._validate_logging())

        # Validate that only the remark field is filled
        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if not self.remark:
                errors["remark"] = ERROR_MESSAGE_NO_REMARK
            if self.source:
                errors["source"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_SET
            if self.source_port_ranges:
                errors["source_port_ranges"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_PORTS_SET
            if self.destination:
                errors["destination"] = ERROR_MESSAGE_ACTION_REMARK_DESTINATION_SET
            if self.destination_port_ranges:
                errors["destination_port_ranges"] = ERROR_MESSAGE_ACTION_REMARK_DESTINATION_PORTS_SET
            if self.protocol:
                errors["protocol"] = ERROR_MESSAGE_ACTION_REMARK_PROTOCOL_SET
        # Validate that the source or destination ports are only set when the protocol is TCP or UDP
        elif self.protocol not in [ACLProtocolChoices.PROTOCOL_TCP, ACLProtocolChoices.PROTOCOL_UDP]:
            if self.source_port_ranges:
                errors["source_port_ranges"] = ERROR_MESSAGE_PROTOCOL_NOT_TCP_OR_UDP_WITH_SOURCE_PORTS_SET
            if self.destination_port_ranges:
                errors["destination_port_ranges"] = ERROR_MESSAGE_PROTOCOL_NOT_TCP_OR_UDP_WITH_DESTINATION_PORTS_SET

        if errors:
            raise ValidationError(errors)

        # Normalize and validate port ranges
        self.source_port_ranges = normalize_port_ranges(self.source_port_ranges or [], "source_port_ranges")
        self.destination_port_ranges = normalize_port_ranges(
            self.destination_port_ranges or [], "destination_port_ranges"
        )
        validate_port_ranges(self.source_port_ranges, "source_port_ranges")
        validate_port_ranges(self.destination_port_ranges, "destination_port_ranges")

    @property
    def destination_port_ranges_list(self):
        """
        Return destination port ranges as a list of strings.

        Ranges are formatted as a single port or as an inclusive
        `"<start>-<end>"` range, e.g. `["22", "80-81", "443"]`.
        """
        return ranges_to_string_list(self.destination_port_ranges)

    @property
    def source_port_ranges_list(self):
        """
        Return source port ranges as a list of strings.

        Ranges are formatted as a single port or as an inclusive
        `"<start>-<end>"` range, e.g. `["22", "80-81", "443"]`.
        """
        return ranges_to_string_list(self.source_port_ranges)

    def get_destination_port_ranges_display(self):
        """
        Return destination port ranges as a comma-separated string.

        Example:
            `"22, 80-81, 443"`
        """
        return ", ".join(self.destination_port_ranges_list)

    def get_source_port_ranges_display(self):
        """
        Return source port ranges as a comma-separated string.

        Example:
            `"22, 80-81, 443"`
        """
        return ", ".join(self.source_port_ranges_list)

    def get_protocol_color(self):
        """
        Return the display color associated with the rule protocol.
        """
        return ACLProtocolChoices.colors.get(self.protocol)


#
# Generic Relations
#

for _rule_model, _role, _accessor in (
    (ACLStandardRule, "source", "accesslist_standard_rule_sources"),
    (ACLExtendedRule, "source", "accesslist_extended_rule_sources"),
    (ACLExtendedRule, "destination", "accesslist_extended_rule_destinations"),
):
    # The query name segment differs from the model name where that runs words together.
    for _model, _query_name in (
        (Aggregate, "aggregate"),
        (IPAddress, "ip_address"),
        (IPRange, "ip_range"),
        (Prefix, "prefix"),
    ):
        GenericRelation(
            to=_rule_model,
            content_type_field=f"{_role}_type",
            object_id_field=f"{_role}_id",
            related_query_name=f"{_role}_{_query_name}",
        ).contribute_to_class(_model, _accessor)
