"""
Define custom model managers for this plugin.
"""

from django.db import models

from utilities.querysets import RestrictedQuerySet

__all__ = ("ACLRuleManager",)


class ACLRuleManager(models.Manager.from_queryset(RestrictedQuerySet)):
    """
    Custom manager for ACL rules providing utility methods.
    """

    def get_next_sequence(self, access_list_id: int, step: int = 10) -> int:
        """
        Return the next available sequence number for a new rule in the given access list.

        Args:
            access_list_id: The ID of the access list to query.
            step: Increment between sequence numbers (default: 10).

        Returns:
            The next sequence number (first rule gets `step`, later rules get `max + step`).
        """
        max_sequence = (
            self.filter(access_list_id=access_list_id).aggregate(max_seq=models.Max("sequence")).get("max_seq")
        )
        return step if max_sequence is None else max_sequence + step
