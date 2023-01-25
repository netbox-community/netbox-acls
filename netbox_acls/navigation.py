"""
Define the plugin menu buttons & the plugin navigation bar enteries.
"""

from django.conf import settings
from extras.plugins import PluginMenu, PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

plugin_settings = settings.PLUGINS_CONFIG["netbox_acls"]

#
# Define plugin menu buttons
#
menu_buttons = (
    PluginMenuItem(
        link="plugins:netbox_acls:accesslist_list",
        link_text="Access Lists",
        permissions=["netbox_acls.view_accesslist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_acls:accesslist_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_acls.add_accesslist"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_acls:aclstandardrule_list",
        link_text="Standard Rules",
        permissions=["netbox_acls.view_aclstandardrule"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_acls:aclstandardrule_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_acls.add_aclstandardrule"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_acls:aclextendedrule_list",
        link_text="Extended Rules",
        permissions=["netbox_acls.view_aclextendedrule"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_acls:aclextendedrule_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_acls.add_aclextendedrule"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_acls:aclinterfaceassignment_list",
        link_text="Interface Assignments",
        permissions=["netbox_acls.view_aclinterfaceassignment"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_acls:aclinterfaceassignment_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_acls.add_aclinterfaceassignment"],
            ),
        ),
    ),
)

if plugin_settings.get("top_level_menu"):
    menu = PluginMenu(
        label="Access Lists",
        groups=(("ACLs", menu_buttons),),
        icon_class="mdi mdi-lock",
    )
else:
    menu_items = menu_buttons
