"""
Utility functions for netbox_acls.
"""

from typing import Iterable

from django.core.exceptions import ValidationError
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.utils.translation import gettext_lazy as _

__all__ = ("normalize_port_ranges",)


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
