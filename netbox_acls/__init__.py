"""
NetBox ACLs Plugin - Manage Access Control Lists in NetBox.
"""

from importlib.metadata import version

from netbox.plugins import PluginConfig

__all__ = ("NetBoxACLsConfig",)


class NetBoxACLsConfig(PluginConfig):
    """
    NetBox plugin configuration for Access Control Lists management.
    """

    name = "netbox_acls"
    verbose_name = "Access Lists"
    version = version("netbox-acls")
    description = "Manage Access Control Lists (ACL) in NetBox"
    base_url = "access-lists"
    min_version = "4.7.0-beta2"
    max_version = "4.7.99"
    default_settings = {
        "rule_sequence_step": 10,
    }


config = NetBoxACLsConfig
