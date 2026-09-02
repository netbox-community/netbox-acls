"""
Utility functions for netbox_acls.
"""

from collections.abc import Iterable

from django.core.exceptions import ValidationError
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.utils.translation import gettext_lazy as _

from .choices import ACLFamilyChoices

__all__ = (
    "infer_family_from_object",
    "normalize_log_options",
    "normalize_port_ranges",
)


def infer_family_from_object(obj):
    """
    Infers the family type (IPv4 or IPv6) from a given object's attributes.
    """
    # Prefer a 'version' if present
    version = (
        getattr(obj, "family", None)
        or getattr(getattr(obj, "prefix", None), "version", None)
        or getattr(getattr(obj, "address", None), "version", None)
        or getattr(getattr(obj, "start_address", None), "version", None)
    )
    if version == 4:
        return ACLFamilyChoices.FAMILY_IPV4
    if version == 6:
        return ACLFamilyChoices.FAMILY_IPV6
    return None


def normalize_log_options(options: Iterable[str]) -> list[str]:
    """
    Deduplicate log options and order them for stable storage and change logging.
    """
    return sorted(set(options))


def normalize_port_ranges(ranges: Iterable[NumericRange], field_name: str = "__all__") -> list[NumericRange]:
    """
    Normalize port ranges to PostgreSQL's canonical half-open [lower, upper) representation,
    sort by lower bound, and merge adjacent ranges.
    """
    normalized = []
    for r in ranges:
        if r.lower is None or r.upper is None:
            raise ValidationError({field_name: _("Range endpoints are required.")})

        lo = r.lower if r.lower_inc else (r.lower + 1)
        hi = (r.upper + 1) if r.upper_inc else r.upper

        # Ensure that the lower endpoint is less than the upper endpoint
        if hi <= lo:
            raise ValidationError(
                {
                    field_name: _("Range start ({start}) cannot be greater than range end ({end}).").format(
                        start=lo, end=hi - 1
                    )
                }
            )

        normalized.append(NumericRange(lo, hi))

    normalized = sorted(normalized, key=lambda rng: (rng.lower, rng.upper))

    collapsed = []
    for r in normalized:
        if not collapsed:
            collapsed.append(r)
            continue

        previous = collapsed[-1]

        if r.lower < previous.upper:
            raise ValidationError({field_name: _("The ranges cannot overlap.")})

        if r.lower == previous.upper:
            collapsed[-1] = NumericRange(previous.lower, r.upper)
            continue

        collapsed.append(r)

    return collapsed
