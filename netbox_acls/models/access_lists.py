"""
Define the django models for this plugin.
"""

from dcim.models import Device, Interface, VirtualChassis
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from virtualization.models import VirtualMachine, VMInterface

from ..choices import ACLActionChoices, ACLAssignmentDirectionChoices, ACLTypeChoices
from ..constants import ACL_HOST_ASSIGNMENT_MODELS, ACL_INTERFACE_ASSIGNMENT_MODELS

__all__ = (
    "AccessList",
    "ACLInterfaceAssignment",
)


alphanumeric_plus = RegexValidator(
    r"^[0-9a-zA-Z,-,_]*$",
    "Only alphanumeric, hyphens, and underscores characters are allowed.",
)


class AccessList(NetBoxModel):
    """
    Model defintion for Access Lists.
    """

    name = models.CharField(
        max_length=500,
        validators=[alphanumeric_plus],
    )
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=ACL_HOST_ASSIGNMENT_MODELS,
        on_delete=models.PROTECT,
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field="assigned_object_type",
        fk_field="assigned_object_id",
    )
    type = models.CharField(
        max_length=30,
        choices=ACLTypeChoices,
    )
    default_action = models.CharField(
        default=ACLActionChoices.ACTION_DENY,
        max_length=30,
        choices=ACLActionChoices,
        verbose_name="Default Action",
    )
    comments = models.TextField(
        blank=True,
    )

    clone_fields = (
        "type",
        "default_action",
    )

    class Meta:
        unique_together = ["assigned_object_type", "assigned_object_id", "name"]
        ordering = ["assigned_object_type", "assigned_object_id", "name"]
        verbose_name = "Access List"
        verbose_name_plural = "Access Lists"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse("plugins:netbox_acls:accesslist", args=[self.pk])

    def get_default_action_color(self):
        return ACLActionChoices.colors.get(self.default_action)

    def get_type_color(self):
        return ACLTypeChoices.colors.get(self.type)


class ACLInterfaceAssignment(NetBoxModel):
    """
    Model defintion for Access Lists associations with other Host interfaces:
      - VM interfaces
      - device interface
      - tbd on more
    """

    access_list = models.ForeignKey(
        on_delete=models.CASCADE,
        to=AccessList,
        verbose_name="Access List",
    )
    direction = models.CharField(
        max_length=30,
        choices=ACLAssignmentDirectionChoices,
    )
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=ACL_INTERFACE_ASSIGNMENT_MODELS,
        on_delete=models.PROTECT,
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field="assigned_object_type",
        fk_field="assigned_object_id",
    )
    comments = models.TextField(
        blank=True,
    )

    clone_fields = ("access_list", "direction")

    class Meta:
        unique_together = [
            "assigned_object_type",
            "assigned_object_id",
            "access_list",
            "direction",
        ]
        ordering = [
            "assigned_object_type",
            "assigned_object_id",
            "access_list",
            "direction",
        ]
        verbose_name = "ACL Interface Assignment"
        verbose_name_plural = "ACL Interface Assignments"

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse(
            "plugins:netbox_acls:aclinterfaceassignment",
            args=[self.pk],
        )

    @classmethod
    def get_prerequisite_models(cls):
        return [AccessList]

    def get_direction_color(self):
        return ACLAssignmentDirectionChoices.colors.get(self.direction)


GenericRelation(
    to=ACLInterfaceAssignment,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="interface",
).contribute_to_class(Interface, "accesslistassignments")

GenericRelation(
    to=ACLInterfaceAssignment,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="vminterface",
).contribute_to_class(VMInterface, "accesslistassignments")

GenericRelation(
    to=AccessList,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="device",
).contribute_to_class(Device, "accesslists")

GenericRelation(
    to=AccessList,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="virtual_chassis",
).contribute_to_class(VirtualChassis, "accesslists")

GenericRelation(
    to=AccessList,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="virtual_machine",
).contribute_to_class(VirtualMachine, "accesslists")
