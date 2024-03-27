"""
Define the NetBox Plugin
"""

from extras.plugins import PluginConfig

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
    min_version = "3.7.0"
    max_version = "3.7.99"


config = NetBoxACLsConfig
