"""
Define the django models for this plugin.
"""

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import ArrayField, IntegerRangeField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.models import PrimaryModel
from utilities.data import ranges_to_string_list

from ..choices import (
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTCPFlagChoices,
    ACLTCPFlagMatchChoices,
    ACLTypeChoices,
)
from ..constants import ACL_RULE_SOURCE_DESTINATION_MODELS
from ..utils import infer_family_from_object, normalize_log_options, normalize_port_ranges, normalize_tcp_flags
from ..validators import validate_port_ranges
from .access_lists import AccessList
from .address_groups import ACLAddressGroup
from .managers import ACLRuleManager
from .mixins import CachedGenericReferenceMixin

__all__ = (
    "ACLExtendedRule",
    "ACLRule",
    "ACLStandardRule",
)


class ACLRule(CachedGenericReferenceMixin, PrimaryModel):
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
    sequence = models.PositiveIntegerField(
        help_text=_("Determines the order of the rule in the ACL processing."),
    )
    description = models.CharField(
        verbose_name=_("Description"),
        max_length=500,
        blank=True,
    )
    action = models.CharField(
        verbose_name=_("Action"),
        max_length=30,
        choices=ACLRuleActionChoices,
        help_text=_("Permit or deny matching traffic. A remark carries a comment only, with no match criteria."),
    )

    # Remark
    remark = models.CharField(
        verbose_name=_("Remark"),
        max_length=500,
        blank=True,
        help_text=_("Free-text comment. Required when the action is remark."),
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
    _source_acladdressgroup = models.ForeignKey(
        to="netbox_acls.acladdressgroup",
        on_delete=models.PROTECT,
        related_name="_%(class)s_sources",
        verbose_name=_("Source Address Group"),
        blank=True,
        null=True,
    )
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
        help_text=_(
            "Optional logging attributes. Leave empty for the target platform's default. "
            "Vendor-specific options are grouped by vendor and are platform-dependent."
        ),
    )

    objects = ACLRuleManager()

    clone_fields = (
        "access_list",
        "action",
        "source",
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

    def _validate_rule_family(self):
        """
        Validates that the ACL rule's family matches the source, destination and protocol families.
        """
        # access_list is non-null, so its descriptor raises rather than returning None when unset.
        if not self.access_list_id:
            return

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

        # Protocol (extended only)
        protocol = getattr(self, "protocol", None)
        if protocol == ACLProtocolChoices.PROTOCOL_ICMPV4:
            families.add(ACLFamilyChoices.FAMILY_IPV4)
        elif protocol == ACLProtocolChoices.PROTOCOL_ICMPV6:
            families.add(ACLFamilyChoices.FAMILY_IPV6)

        # Reject criteria from the other family, or mixed families in a dual-stack ACL
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
            errors["log_options"] = _("Log options require Log matches to be enabled.")

        return errors

    def _validate_remark(self):
        """
        Return field errors for an inconsistent remark rule.
        """
        errors = {}

        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if not self.remark:
                errors["remark"] = _("When the action is 'remark', a remark is required.")
            if self.source:
                errors["source"] = _("When the action is 'remark', the Source must not be set.")
            if self.log_matches:
                errors["log_matches"] = _("When the action is 'remark', Log matches must not be enabled.")
            if self.log_options:
                errors["log_options"] = _("When the action is 'remark', Log options must not be set.")

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
        """

        super().clean()
        errors = {}

        self.log_options = normalize_log_options(self.log_options or [])
        errors.update(self._validate_remark())
        # The remark check already reports every criterion a remark rule sets.
        if self.action != ACLRuleActionChoices.ACTION_REMARK:
            errors.update(self._validate_logging())

        if errors:
            raise ValidationError(errors)


class ACLExtendedRule(ACLRule):
    """
    Inherits ACLRule.

    Add ACLExtendedRule specific fields: source_port_ranges, destination, destination_port_ranges,
    protocol, icmp_type, icmp_code, tcp_flags, and tcp_flags_match
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
        help_text=_("ICMP follows the ACL or address family. ICMPv4 and ICMPv6 select the family explicitly."),
    )

    # Source
    source_port_ranges = ArrayField(
        base_field=IntegerRangeField(),
        verbose_name=_("Source Port Ranges"),
        default=list,
        blank=True,
        help_text=_(
            "Comma-separated port numbers. An inclusive range may be specified using a hyphen "
            "(e.g. 22,80-81,1024-65535). Leave empty to match any port."
        ),
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
        help_text=_(
            "Comma-separated port numbers. An inclusive range may be specified using a hyphen "
            "(e.g. 22,80-81,1024-65535). Leave empty to match any port."
        ),
    )

    # ICMP
    icmp_type = models.PositiveSmallIntegerField(
        verbose_name=_("ICMP Type"),
        blank=True,
        null=True,
        validators=[MaxValueValidator(255)],
        help_text=_(
            "ICMP type number from 0 to 255, interpreted using the rule's IP family. Leave empty to match any type."
        ),
    )
    icmp_code = models.PositiveSmallIntegerField(
        verbose_name=_("ICMP Code"),
        blank=True,
        null=True,
        validators=[MaxValueValidator(255)],
        help_text=_("ICMP code number from 0 to 255. Requires an ICMP type. Leave empty to match any code."),
    )

    # TCP flags
    tcp_flags = ArrayField(
        base_field=models.CharField(
            max_length=30,
            choices=ACLTCPFlagChoices,
        ),
        verbose_name=_("TCP Flags"),
        default=list,
        blank=True,
        help_text=_("Unselected flags are ignored. ACK and RST with Any is the stateless established match."),
    )
    tcp_flags_match = models.CharField(
        verbose_name=_("TCP Flags Match"),
        max_length=30,
        choices=ACLTCPFlagMatchChoices,
        default=ACLTCPFlagMatchChoices.MATCH_ALL,
        help_text=_(
            "All requires every selected flag to be set. Any requires at least one. Ignored when no flags are selected."
        ),
    )

    # Cached related objects by association name for faster access
    _destination_acladdressgroup = models.ForeignKey(
        to="netbox_acls.acladdressgroup",
        on_delete=models.PROTECT,
        related_name="_%(class)s_destinations",
        verbose_name=_("Destination Address Group"),
        blank=True,
        null=True,
    )
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
        "destination",
        "destination_port_ranges",
        "protocol",
        "icmp_type",
        "icmp_code",
        "tcp_flags",
        "tcp_flags_match",
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
        self.tcp_flags = normalize_tcp_flags(self.tcp_flags or [])
        errors.update(self._validate_remark())
        # The remark check already reports every criterion a remark rule sets.
        if self.action != ACLRuleActionChoices.ACTION_REMARK:
            errors.update(self._validate_ports())
            errors.update(self._validate_icmp())
            errors.update(self._validate_tcp_flags())
            errors.update(self._validate_logging())

        if errors:
            raise ValidationError(errors)

        # Normalize and validate port ranges
        self.source_port_ranges = normalize_port_ranges(self.source_port_ranges or [], "source_port_ranges")
        self.destination_port_ranges = normalize_port_ranges(
            self.destination_port_ranges or [], "destination_port_ranges"
        )
        validate_port_ranges(self.source_port_ranges, "source_port_ranges")
        validate_port_ranges(self.destination_port_ranges, "destination_port_ranges")

    def _validate_remark(self):
        """
        Return field errors for an inconsistent remark rule, every extended match criterion included.
        """
        errors = super()._validate_remark()

        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if self.source_port_ranges:
                errors["source_port_ranges"] = _("When the action is 'remark', Source Ports must not be set.")
            if self.destination:
                errors["destination"] = _("When the action is 'remark', the Destination must not be set.")
            if self.destination_port_ranges:
                errors["destination_port_ranges"] = _("When the action is 'remark', Destination Ports must not be set.")
            if self.protocol:
                errors["protocol"] = _("When the action is 'remark', Protocol must not be set.")
            if self.icmp_type is not None:
                errors["icmp_type"] = _("When the action is 'remark', ICMP Type must not be set.")
            if self.icmp_code is not None:
                errors["icmp_code"] = _("When the action is 'remark', ICMP Code must not be set.")
            if self.tcp_flags:
                errors["tcp_flags"] = _("When the action is 'remark', TCP Flags must not be set.")

        return errors

    def _validate_ports(self):
        """
        Return field errors for ports on a protocol other than TCP or UDP.
        """
        errors = {}

        if self.protocol not in [ACLProtocolChoices.PROTOCOL_TCP, ACLProtocolChoices.PROTOCOL_UDP]:
            if self.source_port_ranges:
                errors["source_port_ranges"] = _("Source Ports can only be set when the protocol is TCP or UDP.")
            if self.destination_port_ranges:
                errors["destination_port_ranges"] = _(
                    "Destination Ports can only be set when the protocol is TCP or UDP."
                )

        return errors

    def _validate_icmp(self):
        """
        Return field errors for ICMP criteria lacking an ICMP protocol, a type for a code, or a known family for a type.
        """
        errors = {}

        if self.protocol not in [
            ACLProtocolChoices.PROTOCOL_ICMP,
            ACLProtocolChoices.PROTOCOL_ICMPV4,
            ACLProtocolChoices.PROTOCOL_ICMPV6,
        ]:
            if self.icmp_type is not None:
                errors["icmp_type"] = _("ICMP Type can only be set when the protocol is ICMP, ICMPv4 or ICMPv6.")
            if self.icmp_code is not None:
                errors["icmp_code"] = _("ICMP Code can only be set when the protocol is ICMP, ICMPv4 or ICMPv6.")
        elif self.icmp_type is None and self.icmp_code is not None:
            errors["icmp_code"] = _("ICMP Code requires an ICMP Type.")
        elif (
            self.protocol == ACLProtocolChoices.PROTOCOL_ICMP
            and self.icmp_type is not None
            and self.access_list_id
            and self.access_list.family == ACLFamilyChoices.FAMILY_DUAL
            and not self.source
            and not self.destination
        ):
            errors["icmp_type"] = _(
                "Select ICMPv4 or ICMPv6 when specifying an ICMP Type in a Dual ACL "
                "without address criteria that determine the family."
            )

        return errors

    def _validate_tcp_flags(self):
        """
        Return field errors for TCP flags on a protocol other than TCP.
        """
        errors = {}

        if self.tcp_flags and self.protocol != ACLProtocolChoices.PROTOCOL_TCP:
            errors["tcp_flags"] = _("TCP Flags can only be set when the protocol is TCP.")

        return errors

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

    def get_tcp_flags_match_color(self):
        """
        Return the display color associated with the TCP flag match mode.
        """
        return ACLTCPFlagMatchChoices.colors.get(self.tcp_flags_match)

    @property
    def tcp_flags_badges(self) -> list[tuple[str, str | None]]:
        """
        Return the display label and badge color of each stored TCP flag.
        """
        labels = dict(self._meta.get_field("tcp_flags").base_field.flatchoices)
        colors = ACLTCPFlagChoices.colors
        return [(str(labels.get(value, value)), colors.get(value)) for value in self.tcp_flags]


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
        (ACLAddressGroup, "address_group"),
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
