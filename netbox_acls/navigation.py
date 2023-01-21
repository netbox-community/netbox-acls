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
        link="plugins:netbox_acls:accesslist_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
        permissions=["netbox_acls.add_accesslist"],
    ),
]

aclstandardrule_butons = [
    PluginMenuButton(
        link="plugins:netbox_acls:aclstandardrule_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
        permissions=["netbox_acls.add_aclstandardrule"],
    ),
]

aclextendedrule_butons = [
    PluginMenuButton(
        link="plugins:netbox_acls:aclextendedrule_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
        permissions=["netbox_acls.add_aclextendedrule"],
    ),
]

accesslistassignment_buttons = [
    PluginMenuButton(
        link="plugins:netbox_acls:aclinterfaceassignment_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
        permissions=["netbox_acls.add_aclinterfaceassignment"],
    ),
]

#
# Define navigation bar links including the above buttons defined.
#

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_acls:accesslist_list",
        link_text="Access Lists",
        buttons=accesslist_buttons,
        permissions=["netbox_acls.view_accesslist"],
    ),
    # Comment out Standard Access List rule to force creation in the ACL view
    PluginMenuItem(
        link="plugins:netbox_acls:aclstandardrule_list",
        link_text="ACL Standard Rules",
        buttons=aclstandardrule_butons,
        permissions=["netbox_acls.view_aclstandardrule"],
    ),
    # Comment out Extended Access List rule to force creation in the ACL view
    PluginMenuItem(
        link="plugins:netbox_acls:aclextendedrule_list",
        link_text="ACL Extended Rules",
        buttons=aclextendedrule_butons,
        permissions=["netbox_acls.view_aclextendedrule"],
    ),
    PluginMenuItem(
        link="plugins:netbox_acls:aclinterfaceassignment_list",
        link_text="ACL Interface Assignments",
        buttons=accesslistassignment_buttons,
        permissions=["netbox_acls.view_aclinterfaceassignment"],
    ),
)
