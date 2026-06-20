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
