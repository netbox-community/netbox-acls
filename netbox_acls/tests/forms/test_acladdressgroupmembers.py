from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import Prefix

from ...forms import (
    ACLAddressGroupMemberBulkEditForm,
    ACLAddressGroupMemberFilterForm,
    ACLAddressGroupMemberForm,
    ACLAddressGroupMemberImportForm,
)
from ...models import ACLAddressGroup, ACLAddressGroupMember
from ..views.base import build_ipam_objects
from .base import BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin

UNRESOLVABLE_OBJECT_ID = 99999999


class ACLAddressGroupMemberFormTestCase(BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin, TestCase):
    """Form tests for ACLAddressGroupMember forms."""

    bulk_edit_form = ACLAddressGroupMemberBulkEditForm
    filter_form = ACLAddressGroupMemberFilterForm

    @classmethod
    def setUpTestData(cls):
        cls.aggregate, cls.prefix, cls.ip_address, cls.ip_range = build_ipam_objects()
        cls.ipv6_prefix = Prefix.objects.create(prefix=IPNetwork("2001:db8::/48"))
        cls.address_group = ACLAddressGroup.objects.create(name="trusted-v4")

    def _bound_form(self, member):
        """Bind the form, so the posted member type reaches __init__."""
        return ACLAddressGroupMemberForm(
            data={
                "address_group": self.address_group.pk,
                "member_content_type": ContentType.objects.get_for_model(member).pk,
                "member_object_id": member.pk,
            },
        )

    def test_all_four_member_types(self):
        """Test that every IPAM member type is accepted."""
        for member in (self.prefix, self.aggregate, self.ip_address, self.ip_range):
            with self.subTest(model=member._meta.label_lower):
                form = self._bound_form(member)
                self.assertTrue(form.is_valid(), msg=form.errors.as_text())
                self.assertEqual(form.save().member, member)

    def test_member_types_exclude_address_groups(self):
        """Test that an address group is not offered as a member."""
        queryset = ACLAddressGroupMemberForm().fields["member"].content_type_field.queryset
        self.assertEqual(
            set(queryset.values_list("app_label", "model")),
            {
                ("ipam", "aggregate"),
                ("ipam", "ipaddress"),
                ("ipam", "iprange"),
                ("ipam", "prefix"),
            },
        )

    def test_family_mismatch_returns_form_error(self):
        """Test that a member of another family is rejected as a non-field error."""
        form = self._bound_form(self.ipv6_prefix)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_duplicate_returns_form_error_not_integrity_error(self):
        """Test that a second membership of the same object is rejected before it reaches the database."""
        ACLAddressGroupMember.objects.create(address_group=self.address_group, member=self.prefix)
        form = self._bound_form(self.prefix)
        self.assertFalse(form.is_valid())
        self.assertIn("address_group", form.errors)


class ACLAddressGroupMemberImportFormTestCase(TestCase):
    """Import form tests for ACLAddressGroupMember."""

    @classmethod
    def setUpTestData(cls):
        cls.aggregate, cls.prefix, cls.ip_address, cls.ip_range = build_ipam_objects()
        cls.address_group = ACLAddressGroup.objects.create(name="trusted-v4")

    def _form(self, instance=None, **columns):
        """Build the form from the default row, with None removing a column."""
        data = {
            "address_group": self.address_group.name,
            "member_type": "ipam.prefix",
            "member": str(self.prefix.prefix),
        }
        data.update(columns)
        return ACLAddressGroupMemberImportForm(
            data={key: value for key, value in data.items() if value is not None},
            instance=instance,
        )

    def test_prefix_member_resolves(self):
        """Test that the prefix value is looked up by the prefix field."""
        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().member, self.prefix)

    def test_address_member_resolves(self):
        """Test that the address value is looked up by the address field."""
        form = self._form(member_type="ipam.ipaddress", member=str(self.ip_address.address))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().member, self.ip_address)

    def test_aggregate_member_resolves(self):
        """Test that the aggregate value is looked up by the prefix field."""
        form = self._form(member_type="ipam.aggregate", member=str(self.aggregate.prefix))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().member, self.aggregate)

    def test_ip_range_member_resolves_by_id(self):
        """Test that an IP range, which has no natural value, resolves by member_id."""
        form = self._form(member=None, member_type="ipam.iprange", member_id=str(self.ip_range.pk))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().member, self.ip_range)

    def test_ip_range_value_is_rejected(self):
        """Test that an IP range has no value form and the error names the ID column."""
        form = self._form(member_type="ipam.iprange", member="10.0.1.1-10.0.1.254")
        self.assertFalse(form.is_valid())
        self.assertIn("member_id", str(form.errors["member"]))

    def test_unknown_member_id_is_rejected(self):
        """Test that a member ID matching no object is rejected."""
        form = self._form(member=None, member_id=str(UNRESOLVABLE_OBJECT_ID))
        self.assertFalse(form.is_valid())
        self.assertIn("not found", str(form.errors["member_id"]))

    def test_address_group_member_is_rejected(self):
        """Test that an address group cannot be imported as a member."""
        form = self._form(member=None, member_type="netbox_acls.acladdressgroup", member_id=str(self.address_group.pk))
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid object type", str(form.errors["member_type"]))

    def test_ambiguous_value_is_rejected(self):
        """Test that a value matching two objects is rejected."""
        Prefix.objects.create(prefix=self.prefix.prefix)
        form = self._form()
        self.assertFalse(form.is_valid())
        self.assertIn("Multiple", str(form.errors["member"]))

    def test_member_id_resolves_an_ambiguous_value(self):
        """Test that member_id picks one object where the value matches two."""
        Prefix.objects.create(prefix=self.prefix.prefix)
        form = self._form(member=None, member_id=str(self.prefix.pk))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().member, self.prefix)

    def test_duplicate_is_reported_once(self):
        """Test that importing an existing membership reports one error, on address_group."""
        ACLAddressGroupMember.objects.create(address_group=self.address_group, member=self.prefix)
        form = self._form()
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["address_group"], ["The address group already contains this object."])
        self.assertNotIn("__all__", form.errors)

    def test_metadata_only_import_preserves_reference(self):
        """Test that a comments-only import leaves the member reference unchanged."""
        member = ACLAddressGroupMember.objects.create(address_group=self.address_group, member=self.prefix)
        form = ACLAddressGroupMemberImportForm(data={"comments": "Reviewed"}, instance=member)
        # BulkImportView deletes every field the record omits.
        for name in ("address_group", "member_type", "member", "member_id"):
            del form.fields[name]
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        member.refresh_from_db()
        self.assertEqual(member.member, self.prefix)
        self.assertEqual(member.comments, "Reviewed")
