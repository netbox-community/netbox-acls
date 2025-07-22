"""
Define the NetBox Plugin
"""

from netbox.plugins import PluginConfig
import importlib.metadata

class NetBoxACLsConfig(PluginConfig):
    """
    Plugin specifc configuration
    """

    name = "netbox_acls"
    verbose_name = "Access Lists"
    version = importlib.metadata.version('netbox-acls')
    description = "Manage simple ACLs in NetBox"
    base_url = "access-lists"
    min_version = "4.3.0"
    max_version = "4.3.99"


config = NetBoxACLsConfig
