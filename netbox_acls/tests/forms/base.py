"""
Shared bases for the plugin's form tests.
"""

__all__ = ("BulkEditFieldsetTestMixin",)


class BulkEditFieldsetTestMixin:
    """
    Assert every field a bulk edit form names in its fieldsets exists on the form.

    A fieldset entry with no matching field is dropped silently when the form renders.
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
