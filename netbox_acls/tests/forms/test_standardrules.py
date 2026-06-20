from django.test import TestCase

from ...choices import ACLTypeChoices
from ...forms import ACLStandardRuleBulkEditForm


class ACLStandardRuleFormTestCase(TestCase):
    """Form tests for ACLStandardRule forms."""

    def test_bulkedit_access_list_filtered_to_standard(self):
        """Guard the standard bulk-edit picker the extended form (#360) was copied from."""
        form = ACLStandardRuleBulkEditForm()
        self.assertEqual(
            form.fields["access_list"].query_params,
            {"type": ACLTypeChoices.TYPE_STANDARD},
        )
