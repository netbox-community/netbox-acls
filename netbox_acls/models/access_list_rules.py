"""
Define the django models for this plugin.
"""

from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.urls import reverse
from netbox.models import NetBoxModel
from ipam.models import Prefix, IPRange, IPAddress, Aggregate, Service

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
    Inherrited by both ACLStandardRule and ACLExtendedRule.
    """

    access_list = models.ForeignKey(
        on_delete=models.CASCADE,
        to=AccessList,
        verbose_name="Access List",
        related_name="rules",
    )
    index = models.PositiveIntegerField()
    remark = models.CharField(
        max_length=500,
        blank=True,
    )
    description = models.CharField(
        max_length=500,
        blank=True,
    )
    action = models.CharField(
        choices=ACLRuleActionChoices,
        max_length=30,
    )
    
    source_prefix = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=Prefix,
        verbose_name="Source Prefix",
    )
    source_iprange = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=IPRange,
        verbose_name="Source IP-Range",
    )
    source_ipaddress = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=IPAddress,
        verbose_name="Source IP-Address",
    )
    source_aggregate = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=Aggregate,
        verbose_name="Source Aggregate",
    )
    source_service = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=Service,
        verbose_name="Source Service",
    )

    clone_fields = (
        "access_list", 
        "action", 
        "source_prefix",
        "source_iprange",
        "source_ipaddress",
        "source_aggregate",
        "source_service"
    )

    def __str__(self):
        return f"{self.access_list}: Rule {self.index}"

    def get_action_color(self):
        return ACLRuleActionChoices.colors.get(self.action)

    @classmethod
    def get_prerequisite_models(cls):
        return [
            Prefix, 
            IPRange,
            IPAddress,
            Aggregate,
            Service,
            AccessList
        ]

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


class ACLStandardRule(ACLRule):
    """
    Inherits ACLRule.
    """

    access_list = models.ForeignKey(
        on_delete=models.CASCADE,
        to=AccessList,
        verbose_name="Standard Access List",
        limit_choices_to={"type": ACLTypeChoices.TYPE_STANDARD},
        related_name="aclstandardrules",
    )

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse("plugins:netbox_acls:aclstandardrule", args=[self.pk])

    @classmethod
    def get_prerequisite_models(cls):
        return [
            Prefix, 
            IPRange,
            IPAddress,
            Aggregate,
            Service,
            AccessList
        ]

    class Meta(ACLRule.Meta):
        """
        Define the model properties adding to or overriding the inherited class:
          - default_related_name for any FK relationships
          - verbose name (for displaying in the GUI)
          - verbose name plural (for displaying in the GUI)
        """

        verbose_name = "ACL Standard Rule"
        verbose_name_plural = "ACL Standard Rules"

        constraints = [
            models.CheckConstraint(
                check=(
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=False) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=False) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=False) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=False) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=False)
                    )
                ),
                name='not_more_than_one_source_for_standard_rule'
            )
        ]


class ACLExtendedRule(ACLRule):
    """
    Inherits ACLRule.
    Add ACLExtendedRule specific fields: destination, source_ports, destination_ports and protocol
    """

    access_list = models.ForeignKey(
        on_delete=models.CASCADE,
        to=AccessList,
        verbose_name="Extended Access List",
        limit_choices_to={"type": ACLTypeChoices.TYPE_EXTENDED},
        related_name="aclextendedrules",
    )

    destination_prefix = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=Prefix,
        verbose_name="Destination Prefix",
    )
    destination_iprange = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=IPRange,
        verbose_name="Destination IP-Range",
    )
    destination_ipaddress = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=IPAddress,
        verbose_name="Destination IP-Address",
    )
    destination_aggregate = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=Aggregate,
        verbose_name="Destination Aggregate",
    )
    destination_service = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        to=Service,
        verbose_name="Destination Service",
    )

    source_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        blank=True,
        null=True,
        verbose_name="Source Ports",
    )
    destination_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        blank=True,
        null=True,
        verbose_name="Destination Ports",
    )
    protocol = models.CharField(
        blank=True,
        choices=ACLProtocolChoices,
        max_length=30,
    )

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse("plugins:netbox_acls:aclextendedrule", args=[self.pk])

    def get_protocol_color(self):
        return ACLProtocolChoices.colors.get(self.protocol)

    @classmethod
    def get_prerequisite_models(cls):
        return [
            Prefix, 
            IPRange,
            IPAddress,
            Aggregate,
            Service,
            AccessList
        ]

    class Meta(ACLRule.Meta):
        """
        Define the model properties adding to or overriding the inherited class:
          - default_related_name for any FK relationships
          - verbose name (for displaying in the GUI)
          - verbose name plural (for displaying in the GUI)
        """

        verbose_name = "ACL Extended Rule"
        verbose_name_plural = "ACL Extended Rules"

        constraints = [
            models.CheckConstraint(
                check=(
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=False) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=False) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=False) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=False) & Q(source_service__isnull=True)
                    ) |
                    (
                        Q(source_prefix__isnull=True) & Q(source_iprange__isnull=True) & Q(source_ipaddress__isnull=True) & Q(source_aggregate__isnull=True) & Q(source_service__isnull=False)
                    )
                ),
                name='not_more_than_one_source_for_extended_rule'
            ),
            models.CheckConstraint(
                check=(
                    (
                        Q(destination_prefix__isnull=True) & Q(destination_iprange__isnull=True) & Q(destination_ipaddress__isnull=True) & Q(destination_aggregate__isnull=True) & Q(destination_service__isnull=True)
                    ) |
                    (
                        Q(destination_prefix__isnull=False) & Q(destination_iprange__isnull=True) & Q(destination_ipaddress__isnull=True) & Q(destination_aggregate__isnull=True) & Q(destination_service__isnull=True)
                    ) |
                    (
                        Q(destination_prefix__isnull=True) & Q(destination_iprange__isnull=False) & Q(destination_ipaddress__isnull=True) & Q(destination_aggregate__isnull=True) & Q(destination_service__isnull=True)
                    ) |
                    (
                        Q(destination_prefix__isnull=True) & Q(destination_iprange__isnull=True) & Q(destination_ipaddress__isnull=False) & Q(destination_aggregate__isnull=True) & Q(destination_service__isnull=True)
                    ) |
                    (
                        Q(destination_prefix__isnull=True) & Q(destination_iprange__isnull=True) & Q(destination_ipaddress__isnull=True) & Q(destination_aggregate__isnull=False) & Q(destination_service__isnull=True)
                    ) |
                    (
                        Q(destination_prefix__isnull=True) & Q(destination_iprange__isnull=True) & Q(destination_ipaddress__isnull=True) & Q(destination_aggregate__isnull=True) & Q(destination_service__isnull=False)
                    )
                ),
                name='not_more_than_one_destination_for_extended_rule'
            )
        ]