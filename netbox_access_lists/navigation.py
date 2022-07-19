from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices


accesslist_buttons = [
    PluginMenuButton(
        link='plugins:netbox_access_lists:accesslist_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

aclstandardrule_butons = [
    PluginMenuButton(
        link='plugins:netbox_access_lists:aclstandardrule_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

aclextendedrule_butons = [
    PluginMenuButton(
        link='plugins:netbox_access_lists:aclextendedrule_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_access_lists:accesslist_list',
        link_text='Access-Lists',
        buttons=accesslist_buttons
    ),
    # Comment out Standard Access List Rule to force creation in the ACL view
    PluginMenuItem(
        link='plugins:netbox_access_lists:aclstandardrule_list',
        link_text='Standard Access-List Rules',
        buttons=aclstandardrule_butons
    ),
    # Comment out Extended Access List Rule to force creation in the ACL view
    PluginMenuItem(
        link='plugins:netbox_access_lists:aclextendedrule_list',
        link_text='Extended Access-List Rules',
        buttons=aclextendedrule_butons
    ),
)
