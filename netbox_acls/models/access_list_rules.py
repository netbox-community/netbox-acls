"""
Define the django models for this plugin.
"""

from django.contrib.postgres.fields import ArrayField
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

    def get_protocol_color(self):
        return ACLProtocolChoices.colors.get(self.protocol)
