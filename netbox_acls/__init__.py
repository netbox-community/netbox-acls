"""
Define the NetBox Plugin
"""

import importlib.metadata

from netbox.plugins import PluginConfig


class NetBoxACLsConfig(PluginConfig):
    """
    Plugin specifc configuration
    """

    name = "netbox_acls"
    verbose_name = "Access Lists"
    version = importlib.metadata.version("netbox-acls")
    description = "Manage simple ACLs in NetBox"
    base_url = "access-lists"
    min_version = "4.3.0"
    max_version = "4.4.99"


config = NetBoxACLsConfig
