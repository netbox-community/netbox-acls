"""Convention tests for the create, edit and bulk edit forms.

Every pin here covers a failure mode that renders without an error: a
field built from Django's own classes shows no option descriptions, a
declared choice field drops the label, requirement, default and blank
choice its model field gave it, and a Meta.help_texts entry naming a declared field
never shows.
"""

from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.test import SimpleTestCase
from django.utils.text import capfirst

from utilities.choices import unpack_grouped_choices
from utilities.forms.fields.choices import AttrChoiceMixin

from ...forms import bulk_edit, models


class FormConventionTestCase(SimpleTestCase):
    """Test the choice field conventions of the create, edit and bulk edit forms."""

    @staticmethod
    def _form_classes(*modules):
        """Yield every form class the modules define themselves, in definition order."""
        for module in modules:
            for obj in vars(module).values():
                if isinstance(obj, type) and issubclass(obj, forms.BaseForm) and obj.__module__ == module.__name__:
                    yield obj

    @classmethod
    def _choice_fields(cls, *modules):
        """Yield the form class, name and field of every choice field not backed by a queryset."""
        for form_class in cls._form_classes(*modules):
            for name, field in form_class.base_fields.items():
                if isinstance(field, forms.ChoiceField) and not isinstance(field, forms.ModelChoiceField):
                    yield form_class, name, field

    @classmethod
    def _model_choice_fields(cls):
        """Yield the form class, name, field and model field of every model form choice field."""
        for form_class, name, field in cls._choice_fields(models):
            if not issubclass(form_class, forms.ModelForm):
                continue
            try:
                model_field = form_class._meta.model._meta.get_field(name)
            except FieldDoesNotExist:
                continue
            yield form_class, name, field, model_field

    def test_rendered_choice_fields_are_collected(self):
        """Test that the checks collect every choice field of the model and bulk edit forms."""
        self.assertEqual(len(list(self._choice_fields(models, bulk_edit))), 25)

    def test_rendered_choice_fields_are_description_aware(self):
        """Test that every choice field of the create, edit and bulk edit forms renders descriptions."""
        plain = [
            f"{form_class.__name__}.{name}"
            for form_class, name, field in self._choice_fields(models, bulk_edit)
            if not isinstance(field, AttrChoiceMixin)
        ]
        self.assertEqual(plain, [])

    def test_choice_options_carry_descriptions(self):
        """Test that every option of those fields carries a description, inside groups too."""
        undescribed = [
            f"{form_class.__name__}.{name}={value}"
            for form_class, name, field in self._choice_fields(models, bulk_edit)
            for value, _label in unpack_grouped_choices(field.choices)
            if value not in (None, "") and value not in getattr(field.widget, "descriptions", {})
        ]
        self.assertEqual(undescribed, [])

    def test_model_form_choice_fields_are_collected(self):
        """Test that the checks collect every choice field of the model forms."""
        self.assertEqual(len(list(self._model_choice_fields())), 12)

    def test_choice_fields_keep_the_model_label(self):
        """Test that a choice field keeps the label its model field gives it."""
        relabelled = [
            f"{form_class.__name__}.{name}"
            for form_class, name, field, model_field in self._model_choice_fields()
            if str(field.label) != str(capfirst(model_field.verbose_name))
        ]
        self.assertEqual(relabelled, [])

    def test_choice_fields_keep_the_model_requirement(self):
        """Test that a choice field is required exactly when its model field is not blank."""
        mismatched = [
            f"{form_class.__name__}.{name}"
            for form_class, name, field, model_field in self._model_choice_fields()
            if field.required == model_field.blank
        ]
        self.assertEqual(mismatched, [])

    def test_choice_fields_keep_the_model_default(self):
        """Test that a single choice field starts at the default its model field gives it."""
        mismatched = [
            f"{form_class.__name__}.{name}"
            for form_class, name, field, model_field in self._model_choice_fields()
            if not isinstance(field, forms.MultipleChoiceField)
            and field.initial != (model_field.get_default() if model_field.has_default() else None)
        ]
        self.assertEqual(mismatched, [])

    def test_choice_fields_offer_a_blank_only_without_a_default(self):
        """Test that a single choice field offers a blank only when its model field is blank or has no default."""
        mismatched = [
            f"{form_class.__name__}.{name}"
            for form_class, name, field, model_field in self._model_choice_fields()
            if not isinstance(field, forms.MultipleChoiceField)
            and any(value in (None, "") for value, _label in unpack_grouped_choices(field.choices))
            != (model_field.blank or not model_field.has_default())
        ]
        self.assertEqual(mismatched, [])

    def test_declared_fields_carry_their_own_help_text(self):
        """Test that no Meta.help_texts entry names a declared field, where it would never show."""
        orphaned = [
            f"{form_class.__name__}.{name}"
            for form_class in self._form_classes(models)
            if issubclass(form_class, forms.ModelForm)
            for name in sorted(set(form_class._meta.help_texts or ()) & set(form_class.declared_fields))
        ]
        self.assertEqual(orphaned, [])
