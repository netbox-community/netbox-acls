"""
Define the plugin menu buttons and the plugin navigation bar entries.
"""

from django.conf import settings

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

plugin_settings = settings.PLUGINS_CONFIG["netbox_acls"]

#
# Define plugin menu buttons
#

# Access List
accesslist_item = PluginMenuItem(
    link="plugins:netbox_acls:accesslist_list",
    link_text="Access Lists",
    permissions=["netbox_acls.view_accesslist"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_acls:accesslist_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_acls.add_accesslist"],
        ),
        PluginMenuButton(
            link="plugins:netbox_acls:accesslist_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_acls.add_accesslist"],
        ),
    ),
)

# ACL Standard Rule
aclstandardrule_item = PluginMenuItem(
    link="plugins:netbox_acls:aclstandardrule_list",
    link_text="Standard Rules",
    permissions=["netbox_acls.view_aclstandardrule"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_acls:aclstandardrule_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_acls.add_aclstandardrule"],
        ),
        PluginMenuButton(
            link="plugins:netbox_acls:aclstandardrule_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_acls.add_aclstandardrule"],
        ),
    ),
)

# ACL Extended Rule
aclextendedrule_item = PluginMenuItem(
    link="plugins:netbox_acls:aclextendedrule_list",
    link_text="Extended Rules",
    permissions=["netbox_acls.view_aclextendedrule"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_acls:aclextendedrule_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_acls.add_aclextendedrule"],
        ),
        PluginMenuButton(
            link="plugins:netbox_acls:aclextendedrule_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_acls.add_aclextendedrule"],
        ),
    ),
)

# ACL Assignment
aclassignment_item = PluginMenuItem(
    link="plugins:netbox_acls:aclassignment_list",
    link_text="Assignments",
    permissions=["netbox_acls.view_aclassignment"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_acls:aclassignment_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_acls.add_aclassignment"],
        ),
        PluginMenuButton(
            link="plugins:netbox_acls:aclassignment_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_acls.add_aclassignment"],
        ),
    ),
)


if plugin_settings.get("top_level_menu", True):
    menu = PluginMenu(
        label="Access Lists",
        groups=(
            (
                "Access Lists",
                (
                    accesslist_item,
                    aclassignment_item,
                ),
            ),
            (
                "Rules",
                (
                    aclstandardrule_item,
                    aclextendedrule_item,
                ),
            ),
        ),
        icon_class="mdi mdi-lock",
    )
else:
    menu_items = (
        accesslist_item,
        aclassignment_item,
        aclstandardrule_item,
        aclextendedrule_item,
    )
