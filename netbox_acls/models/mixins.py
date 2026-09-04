"""
Define the model mixins for this plugin.
"""

from utilities.object_types import object_type_identifier

__all__ = ("CachedGenericReferenceMixin",)


class CachedGenericReferenceMixin:
    """
    Maintain the _<role>_<model> shadow columns used by rules and group members.
    """

    # Generic references mirrored into shadow columns, one set per role.
    cached_object_roles = ()

    def cache_related_objects(self, role):
        """
        Refresh one role's shadow IDs.
        """
        # A required content-type FK raises rather than returning None, so gate on its id.
        content_type = getattr(self, f"{role}_type") if getattr(self, f"{role}_type_id") else None
        label = object_type_identifier(content_type) if content_type else None
        object_id = getattr(self, f"{role}_id")
        prefix = f"_{role}_"

        # Copy IDs, not objects: refreshing a shadow must not resolve the GFK again.
        # Shadow columns are located by name, so _<role>_<model> is a contract.
        for field in self._meta.fields:
            if not field.is_relation or not field.name.startswith(prefix):
                continue
            matched = field.related_model._meta.label_lower == label
            setattr(self, field.attname, object_id if matched else None)

    cache_related_objects.alters_data = True
