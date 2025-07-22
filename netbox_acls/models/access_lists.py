"""
Define the django models for this plugin.
"""

from dcim.models import Device, Interface, VirtualChassis
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel
from virtualization.models import VirtualMachine, VMInterface

from ..choices import ACLActionChoices, ACLAssignmentDirectionChoices, ACLTypeChoices
from ..constants import ACL_HOST_ASSIGNMENT_MODELS, ACL_INTERFACE_ASSIGNMENT_MODELS

__all__ = (
    "AccessList",
    "ACLInterfaceAssignment",
)


alphanumeric_plus = RegexValidator(
    r"^[a-zA-Z0-9-_]+$",
    _("Only alphanumeric, hyphens, and underscores characters are allowed."),
)


class AccessList(NetBoxModel):
    """
    Model definition for Access Lists.
    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=500,
        validators=[alphanumeric_plus],
    )
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=ACL_HOST_ASSIGNMENT_MODELS,
        verbose_name=_("Assigned Object Type"),
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field="assigned_object_type",
        fk_field="assigned_object_id",
    )
    type = models.CharField(
        verbose_name=_("Type"),
        max_length=30,
        choices=ACLTypeChoices,
    )
    default_action = models.CharField(
        verbose_name=_("Default Action"),
        max_length=30,
        default=ACLActionChoices.ACTION_DENY,
        choices=ACLActionChoices,
    )
    comments = models.TextField(
        blank=True,
    )

    clone_fields = (
        "default_action",
        "type",
    )

    class Meta:
        unique_together = ["assigned_object_type", "assigned_object_id", "name"]
        ordering = ["assigned_object_type", "assigned_object_id", "name"]
        verbose_name = _("Access List")
        verbose_name_plural = _("Access Lists")

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
    Model definition for Access Lists associations with other Host interfaces:
      - VM interfaces
      - device interface
    """

    access_list = models.ForeignKey(
        to=AccessList,
        on_delete=models.CASCADE,
        verbose_name=_("Access List"),
    )
    direction = models.CharField(
        verbose_name=_("Direction"),
        max_length=30,
        choices=ACLAssignmentDirectionChoices,
    )
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=ACL_INTERFACE_ASSIGNMENT_MODELS,
        verbose_name=_("Assigned Object Type"),
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
    prerequisite_models = ("netbox_acls.AccessList",)

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
        verbose_name = _("ACL Interface Assignment")
        verbose_name_plural = _("ACL Interface Assignments")

    def __str__(self):
        return f"{self.access_list}: Interface {self.assigned_object}"

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse(
            "plugins:netbox_acls:aclinterfaceassignment",
            args=[self.pk],
        )

    def save(self, *args, **kwargs):
        """Saves the current instance to the database."""
        # Ensure the assigned interface's host matches the host assigned to the access list.
        if self.assigned_object.parent_object != self.access_list.assigned_object:
            raise ValidationError(
                {
                    "assigned_object": "The assigned object must be the same as the device assigned to it."
                }
            )

        super().save(*args, **kwargs)

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
