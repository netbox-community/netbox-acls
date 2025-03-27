"""
Define the django models for this plugin.
"""

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ..choices import ACLProtocolChoices, ACLRuleActionChoices, ACLTypeChoices
from .access_lists import AccessList

__all__ = (
    "ACLRule",
    "ACLStandardRule",
    "ACLExtendedRule",
)

# Error message when the action is 'remark', but no remark is provided.
ERROR_MESSAGE_NO_REMARK = _("When the action is 'remark', a remark is required.")

# Error message when the action is 'remark', but the source_prefix is set.
ERROR_MESSAGE_ACTION_REMARK_SOURCE_PREFIX_SET = _("When the action is 'remark', the Source Prefix must not be set.")

# Error message when the action is 'remark', but the source_ports are set.
ERROR_MESSAGE_ACTION_REMARK_SOURCE_PORTS_SET = _("When the action is 'remark', Source Ports must not be set.")

# Error message when the action is 'remark', but the destination_prefix is set.
ERROR_MESSAGE_ACTION_REMARK_DESTINATION_PREFIX_SET = _(
    "When the action is 'remark', the Destination Prefix must not be set."
)

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
    index = models.PositiveIntegerField()
    remark = models.CharField(
        verbose_name=_("Remark"),
        max_length=500,
        blank=True,
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
    )
    source_prefix = models.ForeignKey(
        to="ipam.prefix",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("Source Prefix"),
        blank=True,
        null=True,
    )

    clone_fields = ("access_list", "action", "source_prefix")
    prerequisite_models = ("netbox_acls.AccessList",)

    class Meta:
        """
        Define the common model properties:
          - as an abstract model
          - ordering
          - unique together
        """

        abstract = True
        ordering = ["access_list", "index"]
        unique_together = ["access_list", "index"]

    def __str__(self):
        return f"{self.access_list}: Rule {self.index}"

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse(
            f"plugins:{self._meta.app_label}:{self._meta.model_name}",
            args=[self.pk],
        )

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
        and the source_prefix field must be empty.
        Conversely, if the remark field is provided, the action must be set to 'remark'.
        """

        super().clean()
        errors = {}

        # Validate that only the remark field is filled
        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if not self.remark:
                errors["remark"] = ERROR_MESSAGE_NO_REMARK
            if self.source_prefix:
                errors["source_prefix"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_PREFIX_SET
        # Validate that the action is "remark", when the remark field is provided
        elif self.remark:
            errors["remark"] = ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK

        if errors:
            raise ValidationError(errors)


class ACLExtendedRule(ACLRule):
    """
    Inherits ACLRule.
    Add ACLExtendedRule specific fields: source_ports, destination_prefix, destination_ports, and protocol
    """

    access_list = models.ForeignKey(
        to=AccessList,
        on_delete=models.CASCADE,
        related_name="aclextendedrules",
        limit_choices_to={"type": "extended"},
        verbose_name=_("Extended Access List"),
    )
    source_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        verbose_name=_("Source Ports"),
        blank=True,
        null=True,
    )
    destination_prefix = models.ForeignKey(
        to="ipam.prefix",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("Destination Prefix"),
        blank=True,
        null=True,
    )
    destination_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        verbose_name=_("Destination Ports"),
        blank=True,
        null=True,
    )
    protocol = models.CharField(
        verbose_name=_("Protocol"),
        max_length=30,
        choices=ACLProtocolChoices,
        blank=True,
    )

    clone_fields = (
        "access_list",
        "action",
        "source_prefix",
        "source_ports",
        "destination_prefix",
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

    def clean(self):
        """
        Validate the ACL Extended Rule inputs.

        When the action is 'remark', the remark field must be provided (non-empty),
        and the following fields must be empty:
          - source_prefix
          - source_ports
          - destination_prefix
          - destination_ports
          - protocol

        Conversely, if a remark is provided, the action must be set to 'remark'.
        """
        super().clean()
        errors = {}

        # Validate that only the remark field is filled
        if self.action == ACLRuleActionChoices.ACTION_REMARK:
            if not self.remark:
                errors["remark"] = ERROR_MESSAGE_NO_REMARK
            if self.source_prefix:
                errors["source_prefix"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_PREFIX_SET
            if self.source_ports:
                errors["source_ports"] = ERROR_MESSAGE_ACTION_REMARK_SOURCE_PORTS_SET
            if self.destination_prefix:
                errors["destination_prefix"] = ERROR_MESSAGE_ACTION_REMARK_DESTINATION_PREFIX_SET
            if self.destination_ports:
                errors["destination_ports"] = ERROR_MESSAGE_ACTION_REMARK_DESTINATION_PORTS_SET
            if self.protocol:
                errors["protocol"] = ERROR_MESSAGE_ACTION_REMARK_PROTOCOL_SET
        # Validate that the action is "remark", when the remark field is provided
        elif self.remark:
            errors["remark"] = ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK

        if errors:
            raise ValidationError(errors)

    def get_protocol_color(self):
        return ACLProtocolChoices.colors.get(self.protocol)
