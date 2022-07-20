"""
Define the django models for this plugin.
"""

from dcim.models import Device, VirtualChassis
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from virtualization.models import VirtualMachine

from ..choices import *
from ..constants import ACL_HOST_ASSIGNMENT_MODELS

__all__ = (
    'AccessList',
)


class AccessList(NetBoxModel):
    """
    Model defintion for Access Lists.
    """
    name = models.CharField(
        max_length=100
    )
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=ACL_HOST_ASSIGNMENT_MODELS,
        on_delete=models.PROTECT
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id'
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
        unique_together = ('assigned_object_type', 'assigned_object_id', 'name')
        ordering = ('assigned_object_type', 'assigned_object_id', 'name')
        verbose_name = "Access List"

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


GenericRelation(
    to=AccessList,
    content_type_field='assigned_object_type',
    object_id_field='assigned_object_id',
    related_query_name='device'
).contribute_to_class(Device, 'accesslists')

GenericRelation(
    to=AccessList,
    content_type_field='assigned_object_type',
    object_id_field='assigned_object_id',
    related_query_name='virtual_chassis'
).contribute_to_class(VirtualChassis, 'accesslists')

GenericRelation(
    to=AccessList,
    content_type_field='assigned_object_type',
    object_id_field='assigned_object_id',
    related_query_name='virtual_machine'
).contribute_to_class(VirtualMachine, 'accesslists')
