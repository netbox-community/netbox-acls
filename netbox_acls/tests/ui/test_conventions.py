"""Convention tests for the declarative UI layer.

Every pin here covers a failure mode that still returns 200: a mistyped
panel template renders nothing and raises nothing, a dropped layout
renders an empty page, a surviving retired template silently shadows the
layout that replaced it.
"""

from pathlib import Path

from django.apps import apps
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import SimpleTestCase
from django.urls import reverse

from extras.ui.panels import CustomFieldsPanel, TagsPanel
from netbox.object_actions import AddObject
from netbox.registry import registry
from netbox.ui.layout import SimpleLayout
from netbox.ui.panels import CommentsPanel, ObjectsTablePanel, PluginContentPanel
from utilities.views import get_view

from ... import object_actions

MODELS = tuple(
    sorted(
        apps.get_app_config("netbox_acls").get_models(),
        key=lambda model: model.__name__,
    )
)

# The card header each primary panel is expected to render.
PRIMARY_PANEL_TITLES = {
    "ACLAssignment": "ACL Assignment",
    "ACLExtendedRule": "ACL Extended Rule",
    "ACLStandardRule": "ACL Standard Rule",
    "AccessList": "Access List",
}


class UIConventionTestCase(SimpleTestCase):
    """Test the declarative layout conventions of the detail views."""

    @staticmethod
    def _detail_views():
        """Yield the model and detail view of every plugin model."""
        for model in MODELS:
            yield model, get_view(model)

    @classmethod
    def _panels(cls):
        """Yield the model and every panel its layout declares."""
        for model, view in cls._detail_views():
            for row in view.layout:
                for column in row:
                    for panel in column:
                        yield model, panel

    @staticmethod
    def _primary_panel(model):
        """Return the first panel of a detail view's left column."""
        first_row = next(iter(get_view(model).layout))
        first_column = next(iter(first_row))
        return next(iter(first_column))

    def test_every_model_has_a_ported_detail_view(self):
        """Test no model can ship without a declarative layout."""
        for model in MODELS:
            with self.subTest(model=model.__name__):
                self.assertIsNotNone(getattr(get_view(model), "layout", None))

    def test_detail_views_render_the_generic_template(self):
        """Test every detail view renders the generic object template.

        ObjectView has no template fallback, so a missed one raises
        TemplateDoesNotExist at request time rather than here.
        """
        for model, view in self._detail_views():
            with self.subTest(model=model.__name__):
                self.assertEqual(view.template_name, "generic/object.html")

    def test_layouts_are_simple_layouts(self):
        """Test every layout is the one carrying the plugin content panels."""
        for model, view in self._detail_views():
            with self.subTest(model=model.__name__):
                self.assertIsInstance(view.layout, SimpleLayout)

    def test_retired_detail_templates_are_gone(self):
        """Test no per-model template survives to shadow a layout."""
        for model in MODELS:
            opts = model._meta
            name = f"{opts.app_label}/{opts.model_name}.html"
            with self.subTest(model=model.__name__), self.assertRaises(TemplateDoesNotExist):
                get_template(name)

    def test_template_tree_holds_only_the_expected_directories(self):
        """Test the plugin ships no template outside its own namespace.

        A file under templates/inc/ lands in the namespace NetBox Community
        renders from and shadows it for the whole install. A surviving
        per-model template shadows the layout that replaced it.
        """
        templates = Path(apps.get_app_config("netbox_acls").path) / "templates"

        self.assertEqual(sorted(path.name for path in templates.iterdir()), ["netbox_acls"])
        self.assertEqual(
            sorted(path.name for path in (templates / "netbox_acls").iterdir()),
            ["attrs", "buttons"],
        )

    def test_layouts_declare_the_standard_tail_panels(self):
        """Test every page keeps its custom fields, tags and comments.

        No fixture sets a custom field, a tag or a comment, so a dropped
        panel changes nothing a rendered page asserts. Which column each
        lands in differs per page and is not asserted.
        """
        for model, view in self._detail_views():
            columns = [list(column) for column in list(next(iter(view.layout)))[:2]]
            panels = [panel for column in columns for panel in column]
            with self.subTest(model=model.__name__):
                for panel_class in (CustomFieldsPanel, TagsPanel, CommentsPanel):
                    matches = [panel for panel in panels if isinstance(panel, panel_class)]
                    self.assertEqual(len(matches), 1, panel_class.__name__)
                for column in columns:
                    self.assertIsInstance(column[-1], PluginContentPanel)

    @staticmethod
    def _view_actions():
        """Yield every plugin view and the assignment actions it declares.

        Five of the six tabs hang off core models, so walking the plugin's own
        models reaches none of them. The generic feature views are registered
        by dotted path rather than by class, hence the isinstance guard.
        """
        for models_ in registry["views"].values():
            for entries in models_.values():
                for entry in entries:
                    view = entry["view"]
                    if not isinstance(view, type) or not view.__module__.startswith("netbox_acls."):
                        continue
                    for action in getattr(view, "actions", ()):
                        if isinstance(action, type) and issubclass(action, object_actions.AssignACL):
                            yield view, action

    def test_add_buttons_target_the_views_own_child_model(self):
        """Test every Add button creates what its view is gated on.

        A children view resolves permissions_required against child_model, so
        a button pointing at a different model checks one permission and
        creates another object.
        """
        pairs = list(self._view_actions())

        self.assertEqual(len(pairs), 6)
        for view, action in pairs:
            with self.subTest(view=view.__name__):
                self.assertEqual(apps.get_model(action.child_model_label), view.child_model)

    def test_action_buttons_are_add_actions_with_a_real_template(self):
        """Test every exported action inherits its permission and resolves.

        permissions_required is what a children view maps onto its child
        model, so inheriting AddObject is what keeps the add permission
        correct. ObjectAction.render() goes through render_to_string, so a
        mistyped template is a 500 on all six tabs, not a missing button.
        """
        actions = [getattr(object_actions, name) for name in object_actions.__all__]

        self.assertEqual(len(actions), 2)
        for action in actions:
            with self.subTest(action=action.__name__):
                self.assertTrue(issubclass(action, AddObject))
                self.assertEqual(action.permissions_required, {"add"})
                self.assertEqual(action.get_url(None), reverse("plugins:netbox_acls:aclassignment_add"))
                get_template(action.template_name)

    def test_panel_templates_resolve(self):
        """Test every panel and attribute names a template that exists.

        A mistyped path renders nothing and raises nothing, so the page
        still returns 200 with the card silently missing. Every panel
        template here comes from core, so the attribute templates are
        the only ones this plugin can typo.
        """
        for model, panel in self._panels():
            names = [panel.template_name]
            names += [attr.template_name for attr in getattr(panel, "_attrs", {}).values()]
            for name in names:
                if name is None:
                    continue
                with self.subTest(model=model.__name__, template=name):
                    get_template(name)

    def test_table_panel_filters_are_real_filterset_fields(self):
        """Test every embedded table filter exists on its filterset.

        An unknown filter is ignored, so the card would list every rule
        of that type rather than the access list's own.
        """
        for model, panel in self._panels():
            if not isinstance(panel, ObjectsTablePanel):
                continue
            filterset = get_view(panel.model, "list").filterset
            for key in panel.filters:
                with self.subTest(model=model.__name__, key=key):
                    self.assertIn(key, filterset.base_filters)

    def test_primary_panel_titles_match_the_retired_headers(self):
        """Test each card header still reads as the retired template did."""
        self.assertEqual(
            sorted(PRIMARY_PANEL_TITLES),
            sorted(model.__name__ for model in MODELS),
        )
        for model in MODELS:
            with self.subTest(model=model.__name__):
                self.assertEqual(
                    str(self._primary_panel(model).title),
                    PRIMARY_PANEL_TITLES[model.__name__],
                )
