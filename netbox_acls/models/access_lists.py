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
from ..constants import ACL_ASSIGNMENT_MODELS

__all__ = (
    "AccessList",
    "ACLAssignment",
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
        ordering = ("name",)
        verbose_name = _("Access List")
        verbose_name_plural = _("Access Lists")

    def __str__(self):
        """
        Returns the string representation of the object.
        """
        return self.name

    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the class.
        """
        super().__init__(*args, **kwargs)

        # Save a copy of the ACL name for validation in clean()
        self._original_name = self.__dict__.get("name")

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse("plugins:netbox_acls:accesslist", args=[self.pk])

    def clean(self):
        """
        Override the model's clean method for custom validation.
        """
        super().clean()

        # Validate that uniqueness of the AccessList name per assigned host type
        # (device, virtual chassis, or virtual machine) during renaming.
        if self.pk and self._original_name and self._original_name != self.name:
            host_assigned_object_types = [
                ContentType.objects.get_for_model(Device),
                ContentType.objects.get_for_model(VirtualChassis),
                ContentType.objects.get_for_model(VirtualMachine),
            ]
            acl_assignments = ACLAssignment.objects.filter(
                access_list=self,
                assigned_object_type__in=host_assigned_object_types,
            )
            for acl_assignment in acl_assignments:
                conflicting_acl_assignments = ACLAssignment.objects.filter(
                    access_list__name=self.name,
                    assigned_object_type=acl_assignment.assigned_object_type,
                    assigned_object_id=acl_assignment.assigned_object_id,
                ).exclude(pk=acl_assignment.pk)
                if conflicting_acl_assignments.exists():
                    assigned_object_model = acl_assignment.assigned_object_type.model_class()
                    raise ValidationError(
                        {
                            "name": _(
                                "An Access List with the name '{access_list}' "
                                "is already assigned to the {assigned_object} "
                                "'{assigned_object_name}'.".format(
                                    access_list=self.name,
                                    assigned_object=assigned_object_model._meta.verbose_name,
                                    assigned_object_name=acl_assignment.assigned_object.name,
                                )
                            )
                        }
                    )

    def get_default_action_color(self):
        """
        Retrieves the default action color from the ACLActionChoices.
        """
        return ACLActionChoices.colors.get(self.default_action)

    def get_type_color(self):
        """
        Retrieves the type color from the ACLTypeChoices.
        """
        return ACLTypeChoices.colors.get(self.type)


class ACLAssignment(NetBoxModel):
    """
    Model definition for Access Lists associations with objects:
      - device
      - virtual chassis
      - virtual machine
      - VM interfaces
      - device interface
    """

    access_list = models.ForeignKey(
        to=AccessList,
        on_delete=models.CASCADE,
        related_name="aclassignments",
        verbose_name=_("Access List"),
    )
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=ACL_ASSIGNMENT_MODELS,
        verbose_name=_("Assigned Object Type"),
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field="assigned_object_type",
        fk_field="assigned_object_id",
    )
    direction = models.CharField(
        verbose_name=_("Direction"),
        max_length=30,
        choices=ACLAssignmentDirectionChoices,
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
        verbose_name = _("ACL Assignment")
        verbose_name_plural = _("ACL Assignments")

    def __str__(self):
        """
        Returns the string representation of the object.
        """
        return f"{self.access_list}: Object {self.assigned_object}"

    def get_absolute_url(self):
        """
        The method is a Django convention; although not strictly required,
        it conveniently returns the absolute URL for any particular object.
        """
        return reverse(
            "plugins:netbox_acls:aclassignment",
            args=[self.pk],
        )

    def clean(self) -> None:
        """
        Override the model's clean method for custom validation.
        """

        # Validate object assignment before validation of any other fields
        if self.assigned_object_type and not (self.assigned_object or self.assigned_object_id):
            assigned_object_model = self.assigned_object_type.model_class()
            raise ValidationError(
                {
                    "assigned_object": _(
                        "The {assigned_object} field is required,if an assigned object type is selected.".format(
                            assigned_object=assigned_object_model._meta.verbose_name
                        )
                    )
                }
            )

        super().clean()

        # Validate that uniqueness of the AccessList name per assigned host type
        # (device, virtual chassis, or virtual machine)
        host_assigned_object_types = [
            ContentType.objects.get_for_model(Device),
            ContentType.objects.get_for_model(VirtualChassis),
            ContentType.objects.get_for_model(VirtualMachine),
        ]
        if self.assigned_object_type in host_assigned_object_types:
            self._validate_unique_acl_name_per_assigned_object()
        else:
            self._validate_unique_acl_assignment_per_assigned_interface()

    def _validate_unique_acl_name_per_assigned_object(self) -> None:
        """
        Validates that there is no Access List with the same name for
        the assigned object type and object ID.
        This ensures each ACL name is unique for the same object.
        """
        conflicting_acl_assignments = ACLAssignment.objects.filter(
            access_list__name=self.access_list.name,
            assigned_object_type=self.assigned_object_type,
            assigned_object_id=self.assigned_object_id,
        )
        if self.pk:
            conflicting_acl_assignments = conflicting_acl_assignments.exclude(pk=self.pk)

        if conflicting_acl_assignments.exists():
            assigned_object_model = self.assigned_object_type.model_class()
            raise ValidationError(
                {
                    "access_list": _(
                        "An Access List with the name '{access_list}' "
                        "already exists for the specified "
                        "{assigned_object}.".format(
                            access_list=self.access_list.name, assigned_object=assigned_object_model._meta.verbose_name
                        )
                    )
                }
            )

    def _validate_unique_acl_assignment_per_assigned_interface(self) -> None:
        conflicting_acl_assignments = ACLAssignment.objects.filter(
            assigned_object_type=self.assigned_object_type,
            assigned_object_id=self.assigned_object_id,
            direction=self.direction,
        )
        if self.pk:
            conflicting_acl_assignments = conflicting_acl_assignments.exclude(pk=self.pk)
        if conflicting_acl_assignments.exists():
            assigned_object_model = self.assigned_object_type.model_class()
            raise ValidationError(
                {
                    "direction": _(
                        "An ACL Assignment with the same direction already exists for the specified "
                        "{assigned_object}.".format(assigned_object=assigned_object_model._meta.verbose_name)
                    )
                }
            )

    def save(self, *args, **kwargs):
        """
        Saves the current instance to the database.
        """
        host_assigned_object_types = [
            ContentType.objects.get_for_model(Device),
            ContentType.objects.get_for_model(VirtualChassis),
            ContentType.objects.get_for_model(VirtualMachine),
        ]

        # If the assigned object is a host type (device, virtual chassis,
        # or virtual machine), directional semantics (ingress/egress) are
        # not applicable.
        # Therefore, the direction field is set to "none" in these cases.
        if self.assigned_object_type in host_assigned_object_types:
            self.direction = ACLAssignmentDirectionChoices.DIRECTION_NONE

        super().save(*args, **kwargs)

    def get_direction_color(self):
        """
        Retrieves the direction color from the ACLAssignmentDirectionChoices.
        """
        return ACLAssignmentDirectionChoices.colors.get(self.direction)


GenericRelation(
    to=ACLAssignment,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="interface",
).contribute_to_class(Interface, "aclassignments")

GenericRelation(
    to=ACLAssignment,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="vminterface",
).contribute_to_class(VMInterface, "aclassignments")

GenericRelation(
    to=ACLAssignment,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="device",
).contribute_to_class(Device, "aclassignments")

GenericRelation(
    to=ACLAssignment,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="virtual_chassis",
).contribute_to_class(VirtualChassis, "aclassignments")

GenericRelation(
    to=ACLAssignment,
    content_type_field="assigned_object_type",
    object_id_field="assigned_object_id",
    related_query_name="virtual_machine",
).contribute_to_class(VirtualMachine, "aclassignments")
