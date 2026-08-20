"""
Shared bases for the plugin's form tests.
"""

__all__ = ("BulkEditFieldsetTestMixin",)


class BulkEditFieldsetTestMixin:
    """
    Assert every field a bulk edit form names actually exists on the form.

    A fieldset entry with no matching field is dropped silently when the form
    renders, and a nullable entry with no matching field never clears anything.
    """

    bulk_edit_form = None

    def test_bulkedit_fieldset_fields_all_defined(self):
        """Test that every field named in the bulk-edit fieldsets exists on the form."""
        form = self.bulk_edit_form()
        for fieldset in form.fieldsets:
            for item in fieldset.items:
                if isinstance(item, str):
                    self.assertIn(
                        item,
                        form.fields,
                        msg=f"Fieldset '{fieldset.name}' references undefined field '{item}'",
                    )

    def test_bulkedit_nullable_fields_all_defined(self):
        """Test that every field the bulk-edit form declares as nullable exists on the form."""
        form = self.bulk_edit_form()
        # The class attribute, not the instance one: NetBox appends owner and the
        # custom fields at runtime, and those are core's to guarantee, not ours.
        for name in self.bulk_edit_form.nullable_fields:
            self.assertIn(
                name,
                form.fields,
                msg=f"nullable_fields references undefined field '{name}'",
            )
