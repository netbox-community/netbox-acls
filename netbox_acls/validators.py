"""
Defines validators.
"""

from typing import Iterable

from django.core.exceptions import ValidationError
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.utils.translation import gettext_lazy as _

from .constants import ACL_RULE_PORT_MAX, ACL_RULE_PORT_MIN

__all__ = ("validate_port_ranges",)


def validate_port_ranges(ranges: Iterable[NumericRange], field_name: str = "__all__") -> None:
    """
    Validates that port ranges fall within valid TCP/UDP port limits (1-65535).
    Ranges must already be normalized.
    """
    for r in ranges:
        lo = r.lower
        hi = r.upper - 1

        if lo < ACL_RULE_PORT_MIN or hi > ACL_RULE_PORT_MAX:
            raise ValidationError(
                {
                    field_name: _("Invalid port range ({start}-{end}). Values must be between {min} and {max}.").format(
                        start=lo, end=hi, min=ACL_RULE_PORT_MIN, max=ACL_RULE_PORT_MAX
                    )
                }
            )
