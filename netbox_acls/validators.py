"""
Defines validators.
"""

from .choices import ACLFamilyChoices


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
