"""
Define custom model managers for this plugin.
"""

from django.db import models

from netbox.plugins.utils import get_plugin_config
from utilities.querysets import RestrictedQuerySet

__all__ = ("ACLRuleManager",)

# Plugin name constant to avoid circular imports
PLUGIN_NAME = "netbox_acls"


class ACLRuleManager(models.Manager.from_queryset(RestrictedQuerySet)):
    """
    Custom manager for ACL rules providing utility methods.
    """

    def get_next_sequence(self, access_list_id: int, step: int | None = None) -> int:
        """
        Return the next available sequence number for a new rule in the given access list.

        Args:
            access_list_id: The ID of the access list to query.
            step: Increment between sequence numbers. If None, uses plugin config
                  `rule_sequence_step` (default: 10).

        Returns:
            The next sequence number (first rule gets `step`, later rules get `max + step`).
        """
        if step is None or step <= 0:
            step = get_plugin_config(PLUGIN_NAME, "rule_sequence_step", 10)

        max_sequence = (
            self.filter(access_list_id=access_list_id).aggregate(max_seq=models.Max("sequence")).get("max_seq")
        )
        return step if max_sequence is None else max_sequence + step
