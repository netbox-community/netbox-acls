"""
Define the django models for this plugin.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from ..choices import *

__all__ = (
    'AccessList',
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
