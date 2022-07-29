"""
Define the plugin menu buttons & the plugin navigation bar enteries.
"""

from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

#
# Define plugin menu buttons
#

accesslist_buttons = [
    PluginMenuButton(
        link="plugins:netbox_access_lists:accesslist_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]

aclstandardrule_butons = [
    PluginMenuButton(
        link="plugins:netbox_access_lists:aclstandardrule_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]

aclextendedrule_butons = [
    PluginMenuButton(
        link="plugins:netbox_access_lists:aclextendedrule_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]

accesslistassignment_buttons = [
    PluginMenuButton(
        link="plugins:netbox_access_lists:aclinterfaceassignment_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]

#
# Define navigation bar links including the above buttons defined.
#

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_access_lists:accesslist_list",
        link_text="Access Lists",
        buttons=accesslist_buttons,
    ),
    # Comment out Standard Access List rule to force creation in the ACL view
    PluginMenuItem(
        link="plugins:netbox_access_lists:aclstandardrule_list",
        link_text="ACL Standard Rules",
        buttons=aclstandardrule_butons,
    ),
    # Comment out Extended Access List rule to force creation in the ACL view
    PluginMenuItem(
        link="plugins:netbox_access_lists:aclextendedrule_list",
        link_text="ACL Extended Rules",
        buttons=aclextendedrule_butons,
    ),
    PluginMenuItem(
        link="plugins:netbox_access_lists:aclinterfaceassignment_list",
        link_text="ACL Interface Assignments",
        buttons=accesslistassignment_buttons,
    ),
)
