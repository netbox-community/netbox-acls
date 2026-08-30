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

from extras.ui.panels import CustomFieldsPanel, TagsPanel
from netbox.ui.layout import SimpleLayout
from netbox.ui.panels import CommentsPanel, PluginContentPanel
from utilities.views import get_view

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

    def test_template_directory_holds_only_surviving_partials(self):
        """Test the plugin template directory holds only the attr partials."""
        template_dir = Path(apps.get_app_config("netbox_acls").path) / "templates" / "netbox_acls"

        self.assertEqual(sorted(path.name for path in template_dir.iterdir()), ["attrs"])

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

    def test_panel_templates_resolve(self):
        """Test every panel names a template that exists.

        A mistyped path renders nothing and raises nothing, so the page
        still returns 200 with the card silently missing.
        """
        for model, panel in self._panels():
            if panel.template_name is None:
                continue
            with self.subTest(model=model.__name__, template=panel.template_name):
                get_template(panel.template_name)

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
