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


config = NetBoxAccessListsConfig
