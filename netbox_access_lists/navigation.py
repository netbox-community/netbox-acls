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

#accessliststandardrule_butons = [
#    PluginMenuButton(
#        link='plugins:netbox_access_lists:accessliststandardrule_add',
#        title='Add',
#        icon_class='mdi mdi-plus-thick',
#        color=ButtonColorChoices.GREEN
#    )
#]

accesslistextendedrule_butons = [
    PluginMenuButton(
        link='plugins:netbox_access_lists:accesslistextendedrule_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_access_lists:accesslist_list',
        link_text='Access Lists',
        buttons=accesslist_buttons
    ),
    # # Comment out Standard Access List Rule to force creation in the ACL view
    # PluginMenuItem(
    #     link='plugins:netbox_access_lists:accessliststandardrule_list',
    #     link_text='Access List Rules',
    #     buttons=accessliststandardrule_butons
    # ),
    # # Comment out Extended Access List Rule to force creation in the ACL view
    # PluginMenuItem(
    #     link='plugins:netbox_access_lists:accesslistextendedrule_list',
    #     link_text='Access List Rules',
    #     buttons=accesslistextendedrule_butons
    # ),
)
