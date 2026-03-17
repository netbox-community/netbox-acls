# Add your plugins and plugin settings here.
# Of course uncomment this file out.

# To learn how to build images with your required plugins
# See https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins

PLUGINS = [
    "netbox_acls",
]

PLUGINS_CONFIG = {  # type: ignore
    "netbox_acls": {
        "top_level_menu": True,
        "rule_sequence_step": 10,
    },
}
