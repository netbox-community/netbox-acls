"""
Define the plugin menu buttons & the plugin navigation bar enteries.
"""

from extras.plugins import PluginMenu, PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

#
# Define plugin menu buttons
#

menu = PluginMenu(
    label="Access Lists",
    groups=(
        (
            "ACLs",
            (
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
            ),
        ),
    ),
    icon_class="mdi mdi-lock",
)
