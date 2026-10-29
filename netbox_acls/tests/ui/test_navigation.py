"""Unit tests for the plugin's navigation menu."""

import importlib

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from ... import navigation


class NavigationTestCase(SimpleTestCase):
    def _load(self, top_level_menu):
        """Reload the navigation module under the given top_level_menu setting."""
        plugins_config = {
            **settings.PLUGINS_CONFIG,
            "netbox_acls": {**settings.PLUGINS_CONFIG["netbox_acls"], "top_level_menu": top_level_menu},
        }
        self.addCleanup(importlib.reload, navigation)
        with override_settings(PLUGINS_CONFIG=plugins_config):
            return importlib.reload(navigation)

    def test_groups_section_follows_rules(self):
        """Test the Groups section follows the Rules section."""
        menu = self._load(top_level_menu=True).menu
        self.assertEqual(
            [(group.label, [item.link_text for item in group.items]) for group in menu.groups],
            [
                ("Access Lists", ["Access Lists", "Assignments"]),
                ("Rules", ["Standard Rules", "Extended Rules"]),
                ("Groups", ["Address Groups"]),
            ],
        )

    def test_flat_menu_lists_address_groups_last(self):
        """Test the flat menu lists Address Groups last."""
        items = self._load(top_level_menu=False).menu_items
        self.assertEqual(
            [item.link_text for item in items],
            ["Access Lists", "Assignments", "Standard Rules", "Extended Rules", "Address Groups"],
        )
