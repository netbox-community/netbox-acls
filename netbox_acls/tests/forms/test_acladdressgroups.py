from django import forms
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import Prefix

from ...choices import ACLAddressFamilyChoices
from ...forms import (
    ACLAddressGroupBulkEditForm,
    ACLAddressGroupFilterForm,
    ACLAddressGroupForm,
    ACLAddressGroupImportForm,
)
from ...models import ACLAddressGroup, ACLAddressGroupMember
from .base import BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin


class ACLAddressGroupFormTestCase(BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin, TestCase):
    """Form tests for ACLAddressGroup forms."""

    bulk_edit_form = ACLAddressGroupBulkEditForm
    filter_form = ACLAddressGroupFilterForm

    def test_valid_minimal_form(self):
        """Test that a name and a family are enough to create an address group."""
        form = ACLAddressGroupForm(data={"name": "trusted-v4", "family": ACLAddressFamilyChoices.FAMILY_IPV4})
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        self.assertEqual(form.save().family, ACLAddressFamilyChoices.FAMILY_IPV4)

    def test_dual_family_is_rejected(self):
        """Test that the dual family is not offered to address groups."""
        form = ACLAddressGroupForm(data={"name": "trusted", "family": "dual"})
        self.assertFalse(form.is_valid())
        self.assertIn("family", form.errors)

    def test_duplicate_name_is_rejected(self):
        """Test that address group names are unique."""
        ACLAddressGroup.objects.create(name="trusted-v4")
        form = ACLAddressGroupForm(data={"name": "trusted-v4", "family": ACLAddressFamilyChoices.FAMILY_IPV4})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_choice_filters_accept_multiple_values(self):
        """Test that the filter form's family field is a multi-select, matching the filter set."""
        form = ACLAddressGroupFilterForm()
        self.assertIsInstance(form.fields["family"], forms.MultipleChoiceField)


class ACLAddressGroupImportFormTestCase(TestCase):
    """Import form tests for ACLAddressGroup."""

    def test_blank_family_keeps_the_default(self):
        """Test that a blank family column falls back to IPv4."""
        form = ACLAddressGroupImportForm(data={"name": "imported", "family": ""})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().family, ACLAddressFamilyChoices.FAMILY_IPV4)

    def test_used_group_cannot_change_family(self):
        """Test that the import rejects a family change while the group has members."""
        address_group = ACLAddressGroup.objects.create(name="used")
        prefix = Prefix.objects.create(prefix=IPNetwork("192.0.2.0/24"))
        ACLAddressGroupMember.objects.create(address_group=address_group, member=prefix)
        form = ACLAddressGroupImportForm(
            data={"name": "used", "family": ACLAddressFamilyChoices.FAMILY_IPV6},
            instance=address_group,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("family", form.errors)
