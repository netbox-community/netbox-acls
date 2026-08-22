"""
Define the django models for this plugin.
"""

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, VirtualChassis
from netbox.models import NetBoxModel, PrimaryModel
from netbox.models.mixins import OwnerMixin
from virtualization.models import VirtualMachine, VMInterface

from ..choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ..constants import ACL_ASSIGNMENT_MODELS

__all__ = (
    "ACLAssignment",
    "AccessList",
)


class AccessList(PrimaryModel):
    """
    Model definition for Access Lists.
    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=500,
        validators=[validate_slug],
    )
    type = models.CharField(
        verbose_name=_("Type"),
        max_length=30,
        choices=ACLTypeChoices,
    )
    family = models.CharField(
        verbose_name=_("Family"),
        max_length=8,
        db_index=True,
        default=ACLFamilyChoices.FAMILY_IPV4,
        choices=ACLFamilyChoices,
    )
    default_action = models.CharField(
        verbose_name=_("Default Action"),
        max_length=30,
        default=ACLActionChoices.ACTION_DENY,
        choices=ACLActionChoices,
    )

    clone_fields = (
        "default_action",
        "family",
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

    def clean(self):
        """
        Override the model's clean method for custom validation.
        """
        super().clean()

        original_values = self._get_persisted_values(("name", "type", "family"))

        if original_values:
            # TYPE guard: if any rules exist, forbid changing type
            if original_values["type"] != self.type and self._has_rules():
                raise ValidationError({"type": _("This ACL has ACL rules associated, CANNOT change ACL type.")})

            family_changed = original_values["family"] != self.family

            # FAMILY guard
            if family_changed:
                if self._has_rules():
                    # If any rules exist, forbid changing family
                    raise ValidationError({"family": _("This ACL has ACL rules associated, CANNOT change ACL family.")})
                # Validate family changes for interface assignments
                self._validate_interface_family_conflicts(self.family)
                # Validate host-level duplicate-name constraints under the *new* family
                self._validate_host_name_family_conflicts(self.family, self.name)

            # NAME rename guard
            if not family_changed and original_values["name"] != self.name:
                self._validate_host_name_family_conflicts(self.family, self.name)

    def save(self, *args, **kwargs):
        """
        Override the model's save method for custom validation.
        """
        # update_fields may be any iterable, including a one-shot generator
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = frozenset(update_fields)
            kwargs["update_fields"] = update_fields

        # Repeat the critical guards for callers that skip full_clean(), and
        # if family changes without rules, update assignment families atomically.
        with transaction.atomic():
            original_values = self._get_persisted_values(("type", "family", "name"))
            target_values = self._get_target_values(original_values, update_fields)
            family_changed = False

            if original_values:
                # Re-enforce TYPE guard
                if original_values["type"] != target_values["type"] and self._has_rules():
                    raise ValidationError({"type": _("This ACL has ACL rules associated, CANNOT change ACL type.")})

                # FAMILY change preflight
                if original_values["family"] != target_values["family"]:
                    if self._has_rules():
                        raise ValidationError(
                            {"family": _("This ACL has ACL rules associated, CANNOT change ACL family.")}
                        )
                    # Validate family changes for interface assignments
                    self._validate_interface_family_conflicts(target_values["family"])
                    # Validate host-level duplicate-name constraints under the *new* family
                    self._validate_host_name_family_conflicts(target_values["family"], target_values["name"])
                    family_changed = True

                # NAME rename guard: re-enforce here for callers that skip full_clean().
                if not family_changed and original_values["name"] != target_values["name"]:
                    self._validate_host_name_family_conflicts(target_values["family"], target_values["name"])

            rv = super().save(*args, **kwargs)

            # If family changed (and we passed preflight), mirror it on assignments now
            if family_changed:
                # Sync denormalized family on *all* assignments (host + interface)
                self.aclassignments.update(family=target_values["family"])

            return rv

    def _has_rules(self) -> bool:
        """
        Returns whether this ACL has rules.
        """
        return self.aclstandardrules.exists() or self.aclextendedrules.exists()

    def _get_persisted_values(self, fields=("name", "type", "family")) -> dict:
        """
        Fetch persisted values directly from the DB to compare against current in‑memory changes.
        """
        if not self.pk:
            return {}
        return type(self).objects.filter(pk=self.pk).values(*fields).first() or {}

    def _get_target_values(self, original_values: dict, update_fields: frozenset[str] | None) -> dict:
        """
        Returns the values this save will persist, honoring update_fields.
        """
        return {
            field: getattr(self, field) if update_fields is None or field in update_fields else value
            for field, value in original_values.items()
        }

    def _validate_interface_family_conflicts(self, target_family: str) -> None:
        """
        Validates potential conflicts in interface family assignments within ACL configurations.

        Ensures that assigning a target family to an access control list does not conflict
        with existing interface assignments on the same object and direction.
        """
        interface_assignments = self.aclassignments.exclude(direction=ACLAssignmentDirectionChoices.DIRECTION_NONE)
        for intf_assignment in interface_assignments:
            qs = ACLAssignment.objects.filter(
                assigned_object_type_id=intf_assignment.assigned_object_type_id,
                assigned_object_id=intf_assignment.assigned_object_id,
                direction=intf_assignment.direction,
            ).exclude(access_list=self)

            if target_family == ACLFamilyChoices.FAMILY_DUAL:
                # Dual occupies both family slots → any existing assignment is a conflict
                if qs.exists():
                    raise ValidationError(
                        {
                            "family": _(
                                "Changing to Dual would conflict with an existing interface assignment "
                                "on the same object and direction.",
                            ),
                        },
                    )
            else:
                # v4 conflicts with (v4 or dual); v6 conflicts with (v6 or dual)
                conflict_families = [target_family, ACLFamilyChoices.FAMILY_DUAL]
                if qs.filter(family__in=conflict_families).exists():
                    raise ValidationError(
                        {
                            "family": _(
                                "Changing to {family} would conflict with an existing {family} or "
                                "Dual interface assignment on the same object and direction.",
                            ).format(family=target_family),
                        },
                    )

    def _validate_host_name_family_conflicts(self, target_family: str, target_name: str) -> None:
        """
        Validates that there are no conflicting host assignments for the given target name and family.

        This method checks if there are any Access Control List (ACL) assignments with the
        same name, assigned object type, assigned object ID, and target family that conflict
        with the existing host assignments.
        It raises a validation error in case of conflicts.
        """

        host_assignments = self.aclassignments.filter(direction=ACLAssignmentDirectionChoices.DIRECTION_NONE)
        for host_assignment in host_assignments:
            conflicting_host_assignments = ACLAssignment.objects.filter(
                access_list__name=target_name,
                assigned_object_type=host_assignment.assigned_object_type,
                assigned_object_id=host_assignment.assigned_object_id,
                family=target_family,
            ).exclude(pk=host_assignment.pk)
            if conflicting_host_assignments.exists():
                assigned_object_model = host_assignment.assigned_object_type.model_class()
                raise ValidationError(
                    {
                        "name": _(
                            "An {family} Access List with the name "
                            "'{access_list}' is already assigned to the "
                            "{assigned_object} '{assigned_object_name}'.".format(
                                access_list=target_name,
                                assigned_object=assigned_object_model._meta.verbose_name,
                                assigned_object_name=host_assignment.assigned_object.name,
                                # TODO: Fix formating!
                                family=target_family,
                            ),
                        ),
                    },
                )

    @property
    def is_dual(self) -> bool:
        """
        Returns True if the Access List is dual, False otherwise.
        """
        return self.family == ACLFamilyChoices.FAMILY_DUAL

    @property
    def is_ipv4(self) -> bool:
        """
        Returns True if the Access List is IPv4, False otherwise.
        """
        return self.family == ACLFamilyChoices.FAMILY_IPV4

    @property
    def is_ipv6(self) -> bool:
        """
        Returns True if the Access List is IPv6, False otherwise.
        """
        return self.family == ACLFamilyChoices.FAMILY_IPV6

    def get_default_action_color(self):
        """
        Retrieves the default action color from the ACLActionChoices.
        """
        return ACLActionChoices.colors.get(self.default_action)

    def get_family_color(self):
        """
        Retrieves the family color from the ACLFamilyChoices.
        """
        return ACLFamilyChoices.colors.get(self.family)

    def get_type_color(self):
        """
        Retrieves the type color from the ACLTypeChoices.
        """
        return ACLTypeChoices.colors.get(self.type)


class ACLAssignment(OwnerMixin, NetBoxModel):
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

    # Denormalized family (kept in sync with access_list.family)
    family = models.CharField(
        verbose_name=_("Family"),
        max_length=8,
        db_index=True,
        editable=False,
        choices=ACLFamilyChoices,
    )

    clone_fields = ("access_list", "assigned_object")
    prerequisite_models = ("netbox_acls.AccessList",)

    class Meta:
        constraints = [
            # Prevent the *same ACL* from being assigned twice to the same object+direction
            models.UniqueConstraint(
                fields=["access_list", "assigned_object_type", "assigned_object_id", "direction"],
                name="%(app_label)s_%(class)s_unique_object_direction_family_per_access_list",
                violation_error_message=_("ACL Assignment for the given object and direction."),
            ),
            # Enforce per-family uniqueness ONLY for interface-level (direction != NONE)
            models.UniqueConstraint(
                fields=["assigned_object_type", "assigned_object_id", "direction", "family"],
                condition=~models.Q(direction=ACLAssignmentDirectionChoices.DIRECTION_NONE),
                name="%(app_label)s_%(class)s_unique_object_direction_family_interface_only",
                violation_error_message=_("ACL Assignment for the given object, direction and family exists."),
            ),
        ]
        ordering = [
            "assigned_object_type",
            "assigned_object_id",
            "access_list",
            "family",
            "direction",
        ]
        verbose_name = _("ACL Assignment")
        verbose_name_plural = _("ACL Assignments")

    def __str__(self):
        """
        Returns the string representation of the object.
        """
        return f"{self.access_list}: Object {self.assigned_object}"

    def clean(self) -> None:
        """
        Override the model's clean method for custom validation.
        """

        # Validate object assignment before validation of any other fields
        if self.assigned_object_type_id and not (self.assigned_object or self.assigned_object_id):
            assigned_object_model = self.assigned_object_type.model_class()
            raise ValidationError(
                {
                    "assigned_object": _(
                        "The {assigned_object} field is required,if an assigned object type is selected.".format(
                            assigned_object=assigned_object_model._meta.verbose_name,
                        ),
                    ),
                },
            )

        super().clean()

        # Mirror ACL family to denormalized column, skipping the unset non-null foreign key.
        if self.access_list_id:
            self.family = self.access_list.family

        # Host types carry no directional semantics, so direction is forced to "none".
        host_assigned_object_type_ids = {
            ContentType.objects.get_for_model(model).pk for model in (Device, VirtualChassis, VirtualMachine)
        }
        if self.assigned_object_type_id in host_assigned_object_type_ids:
            self.direction = ACLAssignmentDirectionChoices.DIRECTION_NONE
            self._validate_unique_acl_name_per_assigned_object()
        elif self.assigned_object_type_id:
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
            family=self.family,
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
                        "{assigned_object} and family.".format(
                            access_list=self.access_list.name,
                            assigned_object=assigned_object_model._meta.verbose_name,
                        ),
                    ),
                },
            )

    def _validate_unique_acl_assignment_per_assigned_interface(self) -> None:
        conflicting_acl_assignments = ACLAssignment.objects.filter(
            assigned_object_type=self.assigned_object_type,
            assigned_object_id=self.assigned_object_id,
            direction=self.direction,
        )
        # Enforce: at most one IPv4 and at most one IPv6 per object+direction.
        # A 'dual' ACL conflicts with any existing family at that object+direction.
        if self.family != ACLFamilyChoices.FAMILY_DUAL:
            # v4 conflicts with existing v4 or dual; same for v6
            conflicting_acl_assignments = conflicting_acl_assignments.filter(
                family__in=[self.family, ACLFamilyChoices.FAMILY_DUAL]
            )
        if self.pk:
            conflicting_acl_assignments = conflicting_acl_assignments.exclude(pk=self.pk)
        if conflicting_acl_assignments.exists():
            assigned_object_model = self.assigned_object_type.model_class()
            raise ValidationError(
                {
                    "direction": _(
                        "An ACL Assignment for this family (or a Dual ACL) already exists on the interface "
                        "{assigned_object} and direction.".format(
                            assigned_object=assigned_object_model._meta.verbose_name
                        ),
                    ),
                },
            )

    def save(self, *args, **kwargs):
        """
        Saves the current instance to the database.
        """
        self.family = self.access_list.family

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

        # family is a denormalized copy of access_list.family, so persist them together.
        # direction is derived only for host targets, so it is never promoted here.
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = frozenset(update_fields)
            if update_fields & {"access_list", "access_list_id"}:
                update_fields |= {"family"}
            kwargs["update_fields"] = update_fields

        super().save(*args, **kwargs)

    def get_direction_color(self):
        """
        Retrieves the direction color from the ACLAssignmentDirectionChoices.
        """
        return ACLAssignmentDirectionChoices.colors.get(self.direction)

    def get_family_color(self):
        """
        Retrieves the family color from the ACLFamilyChoices.
        """
        return ACLFamilyChoices.colors.get(self.family)


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
