"""
Define the NetBox Plugin
"""

from netbox.plugins import PluginConfig

from .version import __version__


class NetBoxACLsConfig(PluginConfig):
    """
    Plugin specifc configuration
    """

    name = "netbox_acls"
    verbose_name = "Access Lists"
    version = __version__
    description = "Manage simple ACLs in NetBox"
    base_url = "access-lists"
    min_version = "4.1.0"
    max_version = "4.1.20"


config = NetBoxACLsConfig
