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

accesslistrule_butons = [
    PluginMenuButton(
        link='plugins:netbox_access_lists:accesslistrule_add',
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
    PluginMenuItem(
        link='plugins:netbox_access_lists:accesslistrule_list',
        link_text='Access List Rules',
        buttons=accesslistrule_butons
    ),
)

