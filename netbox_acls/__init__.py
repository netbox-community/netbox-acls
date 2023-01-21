"""
Define the NetBox Plugin
"""

from extras.plugins import PluginConfig


class NetBoxAccessListsConfig(PluginConfig):
    name = "netbox_acls"
    verbose_name = "Access Lists"
    description = "Manage simple ACLs in NetBox"
    version = "1.0.0"
    base_url = "access-lists"
    min_version = "3.4.0"
    max_version = "3.4.99"


config = NetBoxAccessListsConfig
