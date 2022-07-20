"""
Define the django models for this plugin.
"""

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox_access_lists.choices import *

__all__ = (
    'AccessList',
    'ACLStandardRule',
    'ACLExtendedRule',
)


class AccessList(NetBoxModel):
    """
    Model defintion for Access-Lists.
    """
    name = models.CharField(
        max_length=100
    )
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='access_lists'
    )
    type = models.CharField(
        max_length=30,
        choices=ACLTypeChoices
    )
    default_action = models.CharField(
        default=ACLActionChoices.ACTION_DENY,
        max_length=30,
        choices=ACLActionChoices,
        verbose_name='Default Action'
    )
    comments = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ('name', 'device')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse('plugins:netbox_access_lists:accesslist', args=[self.pk])

    def get_default_action_color(self):
        return ACLActionChoices.colors.get(self.default_action)

    def get_type_color(self):
        return ACLTypeChoices.colors.get(self.type)


class ACLRule(NetBoxModel):
    """
    Abstract model for ACL Rules.
    Inherrited by both ACLStandardRule and ACLExtendedRule.
    """
    access_list = models.ForeignKey(
        on_delete=models.CASCADE,
        to=AccessList,
        verbose_name='Access-List',
    )
    index = models.PositiveIntegerField()
    remark = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=500,
        blank=True
    )
    action = models.CharField(
        choices=ACLRuleActionChoices,
        max_length=30,
    )
    source_prefix = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
        to='ipam.Prefix',
        verbose_name='Source Prefix'
    )

    def __str__(self):
        return f'{self.access_list}: Rule {self.index}'

    def get_action_color(self):
        return ACLRuleActionChoices.colors.get(self.action)

    class Meta:
        abstract = True
        default_related_name='%(class)ss'
        ordering = ('access_list', 'index')
        unique_together = ('access_list', 'index')


class ACLStandardRule(ACLRule):
    """
    Inherits ACLRule.
    """

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse('plugins:netbox_access_lists:aclstandardrule', args=[self.pk])


class ACLExtendedRule(ACLRule):
    """
    Inherits ACLRule.
    Add ACLExtendedRule specific fields: source_ports, desintation_prefix, destination_ports, and protocol
    """
    source_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        blank=True,
        null=True,
        verbose_name='Soure Ports'
    )
    destination_prefix = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
        to='ipam.Prefix',
        verbose_name='Destination Prefix'
    )
    destination_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        blank=True,
        null=True,
        verbose_name='Destination Ports'
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
        return reverse('plugins:netbox_access_lists:aclextendedrule', args=[self.pk])

    def get_protocol_color(self):
        return ACLProtocolChoices.colors.get(self.protocol)
