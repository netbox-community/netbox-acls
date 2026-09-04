"""
Define the django models for address groups.
"""

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import models
from django.utils.translation import gettext_lazy as _

from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.models import NetBoxModel, PrimaryModel
from netbox.models.mixins import OwnerMixin
from utilities.data import normalize_update_fields

from ..choices import ACLAddressFamilyChoices
from ..constants import ACL_ADDRESS_OBJECT_MODELS
from ..utils import infer_family_from_object
from .mixins import CachedGenericReferenceMixin

__all__ = (
    "ACLAddressGroup",
    "ACLAddressGroupMember",
)


class ACLAddressGroup(PrimaryModel):
    """
    Model definition for Address Groups.
    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=500,
        unique=True,
        validators=[validate_slug],
    )
    family = models.CharField(
        verbose_name=_("Family"),
        max_length=8,
        db_index=True,
        default=ACLAddressFamilyChoices.FAMILY_IPV4,
        choices=ACLAddressFamilyChoices,
    )

    clone_fields = ("family",)

    class Meta:
        ordering = ("name",)
        verbose_name = _("ACL Address Group")
        verbose_name_plural = _("ACL Address Groups")

    def __str__(self):
        """
        Returns the string representation of the object.
        """
        return self.name

    def clean(self):
        """
        Prevent family changes while members or rules depend on the group.
        """
        super().clean()
        self._validate_family_change()

    def save(self, *args, **kwargs):
        """
        Recheck the family guard for callers that skip full_clean().
        """
        update_fields = normalize_update_fields(kwargs)
        if update_fields is None or "family" in update_fields:
            self._validate_family_change()

        super().save(*args, **kwargs)

    def _validate_family_change(self) -> None:
        """
        Validates that the family only changes on a group without members or rules.
        """
        if not self.pk:
            return
        original_family = type(self).objects.filter(pk=self.pk).values_list("family", flat=True).first()
        if original_family is None or original_family == self.family:
            return
        # Relation managers answer from a prefetch cache when one exists.
        if any(
            type(self).objects.filter(pk=self.pk, **{f"{relation}__isnull": False}).exists()
            for relation in (
                "acladdressgroupmembers",
                "accesslist_standard_rule_sources",
                "accesslist_extended_rule_sources",
                "accesslist_extended_rule_destinations",
            )
        ):
            raise ValidationError(
                {
                    "family": _(
                        "The family cannot change while the address group has members or is used by ACL rules."
                    ),
                }
            )

    def get_family_color(self):
        """
        Retrieves the family color from the ACLAddressFamilyChoices.
        """
        return ACLAddressFamilyChoices.colors.get(self.family)


class ACLAddressGroupMember(CachedGenericReferenceMixin, OwnerMixin, NetBoxModel):
    """
    Model definition for Address Group Members.
    """

    address_group = models.ForeignKey(
        to=ACLAddressGroup,
        on_delete=models.CASCADE,
        related_name="acladdressgroupmembers",
        verbose_name=_("Address Group"),
    )
    member_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=ACL_ADDRESS_OBJECT_MODELS,
        verbose_name=_("Member Type"),
    )
    member_id = models.PositiveBigIntegerField(
        verbose_name=_("Member ID"),
    )
    member = GenericForeignKey(
        ct_field="member_type",
        fk_field="member_id",
    )
    comments = models.TextField(
        blank=True,
    )

    # Cached related objects by association name for faster access
    _member_aggregate = models.ForeignKey(
        to="ipam.aggregate",
        on_delete=models.PROTECT,
        related_name="_acladdressgroupmembers",
        verbose_name=_("Member Aggregate"),
        blank=True,
        null=True,
    )
    _member_ipaddress = models.ForeignKey(
        to="ipam.ipaddress",
        on_delete=models.PROTECT,
        related_name="_acladdressgroupmembers",
        verbose_name=_("Member IP-Address"),
        blank=True,
        null=True,
    )
    _member_iprange = models.ForeignKey(
        to="ipam.iprange",
        on_delete=models.PROTECT,
        related_name="_acladdressgroupmembers",
        verbose_name=_("Member IP-Range"),
        blank=True,
        null=True,
    )
    _member_prefix = models.ForeignKey(
        to="ipam.prefix",
        on_delete=models.PROTECT,
        related_name="_acladdressgroupmembers",
        verbose_name=_("Member Prefix"),
        blank=True,
        null=True,
    )

    clone_fields = ("address_group",)
    prerequisite_models = ("netbox_acls.ACLAddressGroup",)
    cached_object_roles = ("member",)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("address_group", "member_type", "member_id"),
                name="%(app_label)s_%(class)s_unique_member",
                violation_error_message=_("This object is already a member of the address group."),
            ),
        ]
        indexes = (models.Index(fields=("member_type", "member_id")),)
        ordering = ("address_group", "member_type", "member_id")
        verbose_name = _("ACL Address Group Member")
        verbose_name_plural = _("ACL Address Group Members")

    def __str__(self):
        """
        Returns the string representation of the object.
        """
        return f"{self.address_group}: {self.member}"

    def clean(self):
        """
        Override the model's clean method for custom validation.
        """
        # Every later step dereferences member_type, so an unknown or unlisted type stops here.
        if (
            self.member_type_id
            and not ContentType.objects.filter(ACL_ADDRESS_OBJECT_MODELS, pk=self.member_type_id).exists()
        ):
            raise ValidationError(_("Select an Aggregate, IP Address, IP Range, or Prefix as the member type."))
        if self.member_type_id and not (self.member_id or self.member):
            member_type = self.member_type.model_class()
            raise ValidationError(
                {
                    "member": _("Please select a member {member_type}.").format(
                        member_type=member_type._meta.verbose_name
                    )
                }
            )
        super().clean()

        if self.address_group_id and self.member_type_id and self.member_id:
            self._validate_member(self.address_group_id, self.member_type_id, self.member_id)

    def save(self, *args, **kwargs):
        """
        Override the model's save method for custom validation.
        """
        update_fields = normalize_update_fields(kwargs)
        member_written = update_fields is None or bool(update_fields & {"member_type", "member_type_id", "member_id"})

        if member_written or update_fields & {"address_group", "address_group_id"}:
            original_values = {} if update_fields is None else self._get_persisted_values()
            target_values = self._get_target_values(original_values, update_fields)
            self._validate_member(
                target_values["address_group_id"],
                target_values["member_type_id"],
                target_values["member_id"],
            )

        if member_written:
            for role in self.cached_object_roles:
                self.cache_related_objects(role)
            if update_fields is not None:
                # A generic reference is written whole, with its shadow columns.
                kwargs["update_fields"] = update_fields | {
                    "member_type",
                    "member_id",
                    "_member_aggregate",
                    "_member_ipaddress",
                    "_member_iprange",
                    "_member_prefix",
                }

        super().save(*args, **kwargs)

    def to_objectchange(self, action):
        """
        Creates an ObjectChange instance for the address group member.
        """
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.address_group
        return objectchange

    def _get_persisted_values(self, fields=("address_group_id", "member_type_id", "member_id")) -> dict:
        """
        Fetch persisted values directly from the DB to compare against current in-memory changes.
        """
        if not self.pk:
            return {}
        return type(self).objects.filter(pk=self.pk).values(*fields).first() or {}

    def _get_target_values(self, original_values: dict, update_fields: frozenset[str] | None) -> dict:
        """
        Returns the values this save will persist, honoring update_fields.
        """
        target_values = {
            "address_group_id": self.address_group_id,
            "member_type_id": self.member_type_id,
            "member_id": self.member_id,
        }
        if update_fields is None or not original_values:
            return target_values
        if not update_fields & {"address_group", "address_group_id"}:
            target_values["address_group_id"] = original_values["address_group_id"]
        if not update_fields & {"member_type", "member_type_id", "member_id"}:
            target_values["member_type_id"] = original_values["member_type_id"]
            target_values["member_id"] = original_values["member_id"]
        return target_values

    def _validate_member(self, address_group_id: int | None, member_type_id: int | None, member_id: int | None) -> None:
        """
        Validates that the member is a unique, existing address object of the group's family.
        """
        errors = []
        content_type = None
        if isinstance(member_type_id, int) and member_type_id > 0:
            content_type = ContentType.objects.filter(ACL_ADDRESS_OBJECT_MODELS, pk=member_type_id).first()
        if content_type is None:
            errors.append(_("Select an Aggregate, IP Address, IP Range, or Prefix as the member type."))

        member = None
        if not isinstance(member_id, int) or member_id <= 0:
            errors.append(_("A positive member ID is required."))
        elif content_type is not None:
            member = content_type.model_class().objects.filter(pk=member_id).first()
            if member is None:
                errors.append(_("The selected member object does not exist."))

        group_family = None
        if isinstance(address_group_id, int) and address_group_id > 0:
            group_family = ACLAddressGroup.objects.filter(pk=address_group_id).values_list("family", flat=True).first()
        if group_family is None:
            errors.append(_("Select an existing address group."))
        elif member is not None and infer_family_from_object(member) != group_family:
            errors.append(_("The member's IP family must match the address group's family."))

        if errors:
            raise ValidationError(errors)

        duplicates = type(self).objects.filter(
            address_group_id=address_group_id,
            member_type_id=member_type_id,
            member_id=member_id,
        )
        if self.pk:
            duplicates = duplicates.exclude(pk=self.pk)
        if duplicates.exists():
            raise ValidationError({"address_group": _("The address group already contains this object.")})


#
# Generic Relations
#

# The query name segment differs from the model name where that runs words together.
for _model, _query_name in (
    (Aggregate, "aggregate"),
    (IPAddress, "ip_address"),
    (IPRange, "ip_range"),
    (Prefix, "prefix"),
):
    GenericRelation(
        to=ACLAddressGroupMember,
        content_type_field="member_type",
        object_id_field="member_id",
        related_query_name=f"member_{_query_name}",
    ).contribute_to_class(_model, "acladdressgroupmembers")
