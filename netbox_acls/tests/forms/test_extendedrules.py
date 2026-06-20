from django.test import TestCase

from ...choices import ACLTypeChoices
from ...forms import ACLExtendedRuleBulkEditForm


class ACLExtendedRuleFormTestCase(TestCase):
    """Form tests for ACLExtendedRule forms."""

    def test_bulkedit_access_list_filtered_to_extended(self):
        """#360: the extended bulk-edit Access List picker must filter to Extended ACLs."""
        form = ACLExtendedRuleBulkEditForm()
        self.assertEqual(
            form.fields["access_list"].query_params,
            {"type": ACLTypeChoices.TYPE_EXTENDED},
        )

    def test_bulkedit_fieldset_fields_all_defined(self):
        """#361: every field named in the extended bulk-edit fieldsets must exist on the form."""
        form = ACLExtendedRuleBulkEditForm()
        for fieldset in form.fieldsets:
            for item in fieldset.items:
                if isinstance(item, str):
                    self.assertIn(
                        item,
                        form.fields,
                        msg=f"Fieldset '{fieldset.name}' references undefined field '{item}'",
                    )
