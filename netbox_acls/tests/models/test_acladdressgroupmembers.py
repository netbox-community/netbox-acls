from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from netaddr import IPNetwork

from ipam.models import Aggregate, IPAddress, IPRange, Prefix

from ...choices import ACLAddressFamilyChoices
from ...models import ACLAddressGroup, ACLAddressGroupMember
from .base import BaseTestCase


class TestACLAddressGroupMember(BaseTestCase):
    """
    Test ACLAddressGroupMember model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Extend BaseTestCase's setUpTestData() to create additional data for testing.
        """
        super().setUpTestData()

        cls.group = ACLAddressGroup.objects.create(name="v4")
        cls.ipv6_group = ACLAddressGroup.objects.create(name="v6", family=ACLAddressFamilyChoices.FAMILY_IPV6)
        cls.aggregate1_v6 = Aggregate.objects.create(prefix=IPNetwork("2001:db8::/32"), rir=cls.aggregate1.rir)
        cls.ip_address1_v6 = IPAddress.objects.create(address=IPNetwork("2001:db8::1/128"))
        cls.ip_range1_v6 = IPRange.objects.create(
            start_address=IPNetwork("2001:db8::10/64"),
            end_address=IPNetwork("2001:db8::20/64"),
        )

    def test_aggregate_member_is_accepted_in_an_ipv4_group(self):
        """
        Test that an aggregate is accepted as a member of an IPv4 address group.
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.aggregate1)
        member.full_clean()
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member, self.aggregate1)
        self.assertIn(member, self.aggregate1.acladdressgroupmembers.all())
        cached = (
            ACLAddressGroupMember.objects.filter(pk=member.pk)
            .values("_member_aggregate", "_member_ipaddress", "_member_iprange", "_member_prefix")
            .get()
        )
        self.assertEqual(cached["_member_aggregate"], self.aggregate1.pk)
        self.assertIsNone(cached["_member_ipaddress"])
        self.assertIsNone(cached["_member_iprange"])
        self.assertIsNone(cached["_member_prefix"])

    def test_ip_address_member_is_accepted_in_an_ipv4_group(self):
        """
        Test that an IP address is accepted as a member of an IPv4 address group.
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.ip_address1)
        member.full_clean()
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member, self.ip_address1)
        self.assertIn(member, self.ip_address1.acladdressgroupmembers.all())
        cached = (
            ACLAddressGroupMember.objects.filter(pk=member.pk)
            .values("_member_aggregate", "_member_ipaddress", "_member_iprange", "_member_prefix")
            .get()
        )
        self.assertIsNone(cached["_member_aggregate"])
        self.assertEqual(cached["_member_ipaddress"], self.ip_address1.pk)
        self.assertIsNone(cached["_member_iprange"])
        self.assertIsNone(cached["_member_prefix"])

    def test_ip_range_member_is_accepted_in_an_ipv4_group(self):
        """
        Test that an IP range is accepted as a member of an IPv4 address group.
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.ip_range1)
        member.full_clean()
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member, self.ip_range1)
        self.assertIn(member, self.ip_range1.acladdressgroupmembers.all())
        cached = (
            ACLAddressGroupMember.objects.filter(pk=member.pk)
            .values("_member_aggregate", "_member_ipaddress", "_member_iprange", "_member_prefix")
            .get()
        )
        self.assertIsNone(cached["_member_aggregate"])
        self.assertIsNone(cached["_member_ipaddress"])
        self.assertEqual(cached["_member_iprange"], self.ip_range1.pk)
        self.assertIsNone(cached["_member_prefix"])

    def test_prefix_member_is_accepted_in_an_ipv4_group(self):
        """
        Test that a prefix is accepted as a member of an IPv4 address group.
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.prefix1)
        member.full_clean()
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member, self.prefix1)
        self.assertIn(member, self.prefix1.acladdressgroupmembers.all())
        cached = (
            ACLAddressGroupMember.objects.filter(pk=member.pk)
            .values("_member_aggregate", "_member_ipaddress", "_member_iprange", "_member_prefix")
            .get()
        )
        self.assertIsNone(cached["_member_aggregate"])
        self.assertIsNone(cached["_member_ipaddress"])
        self.assertIsNone(cached["_member_iprange"])
        self.assertEqual(cached["_member_prefix"], self.prefix1.pk)

    def test_aggregate_member_is_accepted_in_an_ipv6_group(self):
        """
        Test that an aggregate is accepted as a member of an IPv6 address group.
        """
        member = ACLAddressGroupMember(address_group=self.ipv6_group, member=self.aggregate1_v6)
        member.full_clean()
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member, self.aggregate1_v6)
        self.assertIn(member, self.aggregate1_v6.acladdressgroupmembers.all())
        cached = (
            ACLAddressGroupMember.objects.filter(pk=member.pk)
            .values("_member_aggregate", "_member_ipaddress", "_member_iprange", "_member_prefix")
            .get()
        )
        self.assertEqual(cached["_member_aggregate"], self.aggregate1_v6.pk)
        self.assertIsNone(cached["_member_ipaddress"])
        self.assertIsNone(cached["_member_iprange"])
        self.assertIsNone(cached["_member_prefix"])

    def test_ip_address_member_is_accepted_in_an_ipv6_group(self):
        """
        Test that an IP address is accepted as a member of an IPv6 address group.
        """
        member = ACLAddressGroupMember(address_group=self.ipv6_group, member=self.ip_address1_v6)
        member.full_clean()
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member, self.ip_address1_v6)
        self.assertIn(member, self.ip_address1_v6.acladdressgroupmembers.all())
        cached = (
            ACLAddressGroupMember.objects.filter(pk=member.pk)
            .values("_member_aggregate", "_member_ipaddress", "_member_iprange", "_member_prefix")
            .get()
        )
        self.assertIsNone(cached["_member_aggregate"])
        self.assertEqual(cached["_member_ipaddress"], self.ip_address1_v6.pk)
        self.assertIsNone(cached["_member_iprange"])
        self.assertIsNone(cached["_member_prefix"])

    def test_ip_range_member_is_accepted_in_an_ipv6_group(self):
        """
        Test that an IP range is accepted as a member of an IPv6 address group.
        """
        member = ACLAddressGroupMember(address_group=self.ipv6_group, member=self.ip_range1_v6)
        member.full_clean()
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member, self.ip_range1_v6)
        self.assertIn(member, self.ip_range1_v6.acladdressgroupmembers.all())
        cached = (
            ACLAddressGroupMember.objects.filter(pk=member.pk)
            .values("_member_aggregate", "_member_ipaddress", "_member_iprange", "_member_prefix")
            .get()
        )
        self.assertIsNone(cached["_member_aggregate"])
        self.assertIsNone(cached["_member_ipaddress"])
        self.assertEqual(cached["_member_iprange"], self.ip_range1_v6.pk)
        self.assertIsNone(cached["_member_prefix"])

    def test_prefix_member_is_accepted_in_an_ipv6_group(self):
        """
        Test that a prefix is accepted as a member of an IPv6 address group.
        """
        member = ACLAddressGroupMember(address_group=self.ipv6_group, member=self.prefix1_v6)
        member.full_clean()
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member, self.prefix1_v6)
        self.assertIn(member, self.prefix1_v6.acladdressgroupmembers.all())
        cached = (
            ACLAddressGroupMember.objects.filter(pk=member.pk)
            .values("_member_aggregate", "_member_ipaddress", "_member_iprange", "_member_prefix")
            .get()
        )
        self.assertIsNone(cached["_member_aggregate"])
        self.assertIsNone(cached["_member_ipaddress"])
        self.assertIsNone(cached["_member_iprange"])
        self.assertEqual(cached["_member_prefix"], self.prefix1_v6.pk)

    def test_all_ipam_targets_are_protected(self):
        """
        Test that an IPAM object cannot be deleted while it is a member.
        """
        for target in (self.aggregate1, self.ip_address1, self.ip_range1, self.prefix1):
            with self.subTest(model=target._meta.label_lower):
                ACLAddressGroupMember.objects.create(address_group=self.group, member=target)
                with self.assertRaises(ProtectedError):
                    target.delete()

    def test_aggregate_family_mismatch_rejected_by_clean(self):
        """
        Test that an IPv6 aggregate is rejected as a member of an IPv4 address group by clean().
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.aggregate1_v6)
        with self.assertRaises(ValidationError):
            member.full_clean()

    def test_aggregate_family_mismatch_rejected_by_save(self):
        """
        Test that an IPv6 aggregate is rejected as a member of an IPv4 address group by save().
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.aggregate1_v6)
        with self.assertRaises(ValidationError):
            member.save()

    def test_ip_address_family_mismatch_rejected_by_clean(self):
        """
        Test that an IPv6 IP address is rejected as a member of an IPv4 address group by clean().
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.ip_address1_v6)
        with self.assertRaises(ValidationError):
            member.full_clean()

    def test_ip_address_family_mismatch_rejected_by_save(self):
        """
        Test that an IPv6 IP address is rejected as a member of an IPv4 address group by save().
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.ip_address1_v6)
        with self.assertRaises(ValidationError):
            member.save()

    def test_ip_range_family_mismatch_rejected_by_clean(self):
        """
        Test that an IPv6 IP range is rejected as a member of an IPv4 address group by clean().
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.ip_range1_v6)
        with self.assertRaises(ValidationError):
            member.full_clean()

    def test_ip_range_family_mismatch_rejected_by_save(self):
        """
        Test that an IPv6 IP range is rejected as a member of an IPv4 address group by save().
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.ip_range1_v6)
        with self.assertRaises(ValidationError):
            member.save()

    def test_prefix_family_mismatch_rejected_by_clean(self):
        """
        Test that an IPv6 prefix is rejected as a member of an IPv4 address group by clean().
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.prefix1_v6)
        with self.assertRaises(ValidationError):
            member.full_clean()

    def test_prefix_family_mismatch_rejected_by_save(self):
        """
        Test that an IPv6 prefix is rejected as a member of an IPv4 address group by save().
        """
        member = ACLAddressGroupMember(address_group=self.group, member=self.prefix1_v6)
        with self.assertRaises(ValidationError):
            member.save()

    def test_nesting_rejected_by_clean(self):
        """
        Test that an address group is rejected as a member by clean().
        """
        peer = ACLAddressGroup.objects.create(name="peer", family=self.group.family)
        member = ACLAddressGroupMember(address_group=self.group, member=peer)
        with self.assertRaises(ValidationError) as ctx:
            member.full_clean()
        self.assertIn(
            "Select an Aggregate, IP Address, IP Range, or Prefix as the member type.",
            ctx.exception.message_dict[NON_FIELD_ERRORS],
        )

    def test_nesting_rejected_by_save(self):
        """
        Test that an address group is rejected as a member by save().
        """
        peer = ACLAddressGroup.objects.create(name="peer", family=self.group.family)
        member = ACLAddressGroupMember(address_group=self.group, member=peer)
        with self.assertRaises(ValidationError):
            member.save()

    def test_empty_member_rejected_by_clean(self):
        """
        Test that an empty membership gets field errors and no non-field error.
        """
        member = ACLAddressGroupMember()
        with self.assertRaises(ValidationError) as ctx:
            member.full_clean()
        self.assertIn("address_group", ctx.exception.message_dict)
        self.assertNotIn(NON_FIELD_ERRORS, ctx.exception.message_dict)

    def test_empty_member_rejected_by_save(self):
        """
        Test that an empty membership raises ValidationError in save().
        """
        member = ACLAddressGroupMember()
        with self.assertRaises(ValidationError):
            member.save()

    def test_member_without_type_and_id_rejected_by_clean(self):
        """
        Test that a membership with only a group gets field errors and no non-field error.
        """
        member = ACLAddressGroupMember(address_group=self.group)
        with self.assertRaises(ValidationError) as ctx:
            member.full_clean()
        self.assertIn("member_type", ctx.exception.message_dict)
        self.assertNotIn(NON_FIELD_ERRORS, ctx.exception.message_dict)

    def test_member_without_type_and_id_rejected_by_save(self):
        """
        Test that a membership with only a group raises ValidationError in save().
        """
        member = ACLAddressGroupMember(address_group=self.group)
        with self.assertRaises(ValidationError):
            member.save()

    def test_member_without_id_rejected_by_clean(self):
        """
        Test that a membership with a type but no id raises ValidationError in clean().
        """
        member = ACLAddressGroupMember(
            address_group=self.group,
            member_type=ContentType.objects.get_for_model(Prefix),
        )
        with self.assertRaises(ValidationError) as ctx:
            member.full_clean()
        self.assertIn("member", ctx.exception.message_dict)

    def test_member_without_id_rejected_by_save(self):
        """
        Test that a membership with a type but no id raises ValidationError in save().
        """
        member = ACLAddressGroupMember(
            address_group=self.group,
            member_type=ContentType.objects.get_for_model(Prefix),
        )
        with self.assertRaises(ValidationError):
            member.save()

    def test_member_without_type_rejected_by_clean(self):
        """
        Test that a membership with an id but no type raises ValidationError in clean().
        """
        member = ACLAddressGroupMember(address_group=self.group, member_id=self.prefix1.pk)
        with self.assertRaises(ValidationError):
            member.full_clean()

    def test_member_without_type_rejected_by_save(self):
        """
        Test that a membership with an id but no type raises ValidationError in save().
        """
        member = ACLAddressGroupMember(address_group=self.group, member_id=self.prefix1.pk)
        with self.assertRaises(ValidationError):
            member.save()

    def test_member_with_missing_object_rejected_by_clean(self):
        """
        Test that a membership pointing at a missing object raises ValidationError in clean().
        """
        member = ACLAddressGroupMember(
            address_group=self.group,
            member_type=ContentType.objects.get_for_model(Prefix),
            member_id=999999999,
        )
        with self.assertRaises(ValidationError):
            member.full_clean()

    def test_member_with_missing_object_rejected_by_save(self):
        """
        Test that a membership pointing at a missing object raises ValidationError in save().
        """
        member = ACLAddressGroupMember(
            address_group=self.group,
            member_type=ContentType.objects.get_for_model(Prefix),
            member_id=999999999,
        )
        with self.assertRaises(ValidationError):
            member.save()

    def test_member_with_missing_type_rejected_by_clean(self):
        """
        Test that a membership with an unknown type raises ValidationError in clean().
        """
        member = ACLAddressGroupMember(address_group=self.group, member_type_id=999999999, member_id=1)
        with self.assertRaises(ValidationError) as ctx:
            member.full_clean()
        self.assertIn(
            "Select an Aggregate, IP Address, IP Range, or Prefix as the member type.",
            ctx.exception.message_dict[NON_FIELD_ERRORS],
        )

    def test_member_with_missing_type_and_no_id_rejected_by_clean(self):
        """
        Test that a membership with an unknown type and no id raises ValidationError in clean().
        """
        member = ACLAddressGroupMember(address_group=self.group, member_type_id=999999999)
        with self.assertRaises(ValidationError) as ctx:
            member.full_clean()
        self.assertIn(
            "Select an Aggregate, IP Address, IP Range, or Prefix as the member type.",
            ctx.exception.message_dict[NON_FIELD_ERRORS],
        )

    def test_member_with_missing_type_rejected_by_save(self):
        """
        Test that a membership with an unknown type raises ValidationError in save().
        """
        member = ACLAddressGroupMember(address_group=self.group, member_type_id=999999999, member_id=1)
        with self.assertRaises(ValidationError):
            member.save()

    def test_member_with_missing_group_rejected_by_clean(self):
        """
        Test that a membership with an unknown group raises ValidationError in clean().
        """
        member = ACLAddressGroupMember(address_group_id=999999999, member=self.prefix1)
        with self.assertRaises(ValidationError) as ctx:
            member.full_clean()
        self.assertIn("Select an existing address group.", ctx.exception.message_dict[NON_FIELD_ERRORS])

    def test_member_with_missing_group_rejected_by_save(self):
        """
        Test that a membership with an unknown group raises ValidationError in save().
        """
        member = ACLAddressGroupMember(address_group_id=999999999, member=self.prefix1)
        with self.assertRaises(ValidationError):
            member.save()

    def test_exact_duplicate_rejected_by_clean(self):
        """
        Test that clean() reports a duplicate membership once, on the address group.
        """
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        duplicate = ACLAddressGroupMember(address_group=self.group, member=self.prefix1)
        with self.assertRaises(ValidationError) as ctx:
            duplicate.full_clean()
        self.assertEqual(
            ctx.exception.message_dict,
            {"address_group": ["The address group already contains this object."]},
        )

    def test_exact_duplicate_rejected_by_save(self):
        """
        Test that a duplicate membership raises ValidationError in save(), never an IntegrityError.
        """
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        duplicate = ACLAddressGroupMember(address_group=self.group, member=self.prefix1)
        with self.assertRaises(ValidationError):
            duplicate.save()

    def test_database_uniqueness_also_guards_bulk_writes(self):
        """
        Test that the database constraint rejects a duplicate that bypasses validation.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        duplicate = ACLAddressGroupMember(address_group=self.group, member=self.prefix1)
        duplicate.cache_related_objects("member")
        with self.assertRaises(IntegrityError), transaction.atomic():
            ACLAddressGroupMember.objects.bulk_create([duplicate])
        self.assertTrue(ACLAddressGroupMember.objects.filter(pk=member.pk).exists())

    def test_overlapping_members_are_allowed_in_one_group(self):
        """
        Test that overlapping prefixes can be members of the same address group.
        """
        child = Prefix.objects.create(prefix=IPNetwork("10.1.1.0/24"))
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member = ACLAddressGroupMember(address_group=self.group, member=child)
        member.full_clean()
        member.save()
        self.assertEqual(self.group.acladdressgroupmembers.count(), 2)

    def test_reuse_across_groups_is_allowed(self):
        """
        Test that one object can be a member of several address groups.
        """
        another = ACLAddressGroup.objects.create(name="another-v4")
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member = ACLAddressGroupMember(address_group=another, member=self.prefix1)
        member.full_clean()
        member.save()
        self.assertEqual(self.prefix1.acladdressgroupmembers.count(), 2)

    def test_change_log_points_to_group(self):
        """
        Test that membership changes are logged against the parent group.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        self.assertEqual(member.to_objectchange("create").related_object, self.group)

    def test_member_clone_keeps_parent_but_not_duplicate_reference(self):
        """
        Test that cloning a membership keeps the group but not the member reference.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        attrs = member.clone()
        self.assertEqual(attrs["address_group"], self.group.pk)
        self.assertNotIn("member_content_type", attrs)
        self.assertNotIn("member_object_id", attrs)

    def test_member_move_revalidates_family(self):
        """
        Test that moving a membership to a group of another family is rejected.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.address_group = self.ipv6_group
        with self.assertRaises(ValidationError):
            member.save()

    def test_retargeting_a_reference_clears_the_old_shadow(self):
        """
        Test that retargeting a membership clears the previous shadow column.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.member = self.ip_address1
        member.save()
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_ipaddress", "_member_prefix").get()
        self.assertIsNone(cached["_member_prefix"])
        self.assertEqual(cached["_member_ipaddress"], self.ip_address1.pk)

    def test_partial_save_of_member_id_retargets_prefix_to_ip_address(self):
        """
        Test that saving member_id alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.address_group = self.ipv6_group
        member.member = self.ip_address1
        member.save(update_fields={"member_id"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.ip_address1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_ipaddress", "_member_prefix").get()
        self.assertEqual(cached["_member_ipaddress"], self.ip_address1.pk)
        self.assertIsNone(cached["_member_prefix"])

    def test_partial_save_of_member_type_retargets_prefix_to_ip_address(self):
        """
        Test that saving member_type alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.address_group = self.ipv6_group
        member.member = self.ip_address1
        member.save(update_fields={"member_type"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.ip_address1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_ipaddress", "_member_prefix").get()
        self.assertEqual(cached["_member_ipaddress"], self.ip_address1.pk)
        self.assertIsNone(cached["_member_prefix"])

    def test_partial_save_of_member_type_id_retargets_prefix_to_ip_address(self):
        """
        Test that saving member_type_id alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.address_group = self.ipv6_group
        member.member = self.ip_address1
        member.save(update_fields={"member_type_id"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.ip_address1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_ipaddress", "_member_prefix").get()
        self.assertEqual(cached["_member_ipaddress"], self.ip_address1.pk)
        self.assertIsNone(cached["_member_prefix"])

    def test_partial_save_of_one_shot_member_id_retargets_prefix_to_ip_address(self):
        """
        Test that a one-shot update_fields naming member_id writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.address_group = self.ipv6_group
        member.member = self.ip_address1
        member.save(update_fields=iter(["member_id"]))

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.ip_address1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_ipaddress", "_member_prefix").get()
        self.assertEqual(cached["_member_ipaddress"], self.ip_address1.pk)
        self.assertIsNone(cached["_member_prefix"])

    def test_partial_save_of_member_id_retargets_aggregate_to_ip_range(self):
        """
        Test that saving member_id alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.aggregate1)
        member.address_group = self.ipv6_group
        member.member = self.ip_range1
        member.save(update_fields={"member_id"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.ip_range1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_iprange", "_member_aggregate").get()
        self.assertEqual(cached["_member_iprange"], self.ip_range1.pk)
        self.assertIsNone(cached["_member_aggregate"])

    def test_partial_save_of_member_type_retargets_aggregate_to_ip_range(self):
        """
        Test that saving member_type alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.aggregate1)
        member.address_group = self.ipv6_group
        member.member = self.ip_range1
        member.save(update_fields={"member_type"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.ip_range1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_iprange", "_member_aggregate").get()
        self.assertEqual(cached["_member_iprange"], self.ip_range1.pk)
        self.assertIsNone(cached["_member_aggregate"])

    def test_partial_save_of_member_type_id_retargets_aggregate_to_ip_range(self):
        """
        Test that saving member_type_id alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.aggregate1)
        member.address_group = self.ipv6_group
        member.member = self.ip_range1
        member.save(update_fields={"member_type_id"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.ip_range1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_iprange", "_member_aggregate").get()
        self.assertEqual(cached["_member_iprange"], self.ip_range1.pk)
        self.assertIsNone(cached["_member_aggregate"])

    def test_partial_save_of_one_shot_member_id_retargets_aggregate_to_ip_range(self):
        """
        Test that a one-shot update_fields naming member_id writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.aggregate1)
        member.address_group = self.ipv6_group
        member.member = self.ip_range1
        member.save(update_fields=iter(["member_id"]))

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.ip_range1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_iprange", "_member_aggregate").get()
        self.assertEqual(cached["_member_iprange"], self.ip_range1.pk)
        self.assertIsNone(cached["_member_aggregate"])

    def test_partial_save_of_member_id_retargets_ip_range_to_aggregate(self):
        """
        Test that saving member_id alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.ip_range1)
        member.address_group = self.ipv6_group
        member.member = self.aggregate1
        member.save(update_fields={"member_id"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.aggregate1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_aggregate", "_member_iprange").get()
        self.assertEqual(cached["_member_aggregate"], self.aggregate1.pk)
        self.assertIsNone(cached["_member_iprange"])

    def test_partial_save_of_member_type_retargets_ip_range_to_aggregate(self):
        """
        Test that saving member_type alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.ip_range1)
        member.address_group = self.ipv6_group
        member.member = self.aggregate1
        member.save(update_fields={"member_type"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.aggregate1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_aggregate", "_member_iprange").get()
        self.assertEqual(cached["_member_aggregate"], self.aggregate1.pk)
        self.assertIsNone(cached["_member_iprange"])

    def test_partial_save_of_member_type_id_retargets_ip_range_to_aggregate(self):
        """
        Test that saving member_type_id alone writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.ip_range1)
        member.address_group = self.ipv6_group
        member.member = self.aggregate1
        member.save(update_fields={"member_type_id"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.aggregate1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_aggregate", "_member_iprange").get()
        self.assertEqual(cached["_member_aggregate"], self.aggregate1.pk)
        self.assertIsNone(cached["_member_iprange"])

    def test_partial_save_of_one_shot_member_id_retargets_ip_range_to_aggregate(self):
        """
        Test that a one-shot update_fields naming member_id writes the whole pair and refreshes the shadow columns.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.ip_range1)
        member.address_group = self.ipv6_group
        member.member = self.aggregate1
        member.save(update_fields=iter(["member_id"]))

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.aggregate1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_aggregate", "_member_iprange").get()
        self.assertEqual(cached["_member_aggregate"], self.aggregate1.pk)
        self.assertIsNone(cached["_member_iprange"])

    def test_member_reference_partial_save_is_validated(self):
        """
        Test that a partial save of the member reference is validated.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.member = self.prefix1_v6
        with self.assertRaises(ValidationError):
            member.save(update_fields={"member_id"})

    def test_group_only_save_validates_the_stored_member(self):
        """
        Test that a group-only partial save is validated against the stored member.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        for update_fields in ({"address_group"}, {"address_group_id"}):
            with self.subTest(update_fields=update_fields):
                member.address_group = self.ipv6_group
                member.member = self.prefix1_v6
                with self.assertRaises(ValidationError):
                    member.save(update_fields=update_fields)
        member.refresh_from_db()
        self.assertEqual(member.address_group, self.group)
        self.assertEqual(member.member, self.prefix1)

    def test_group_only_save_leaves_a_dirty_member_unwritten(self):
        """
        Test that a group-only partial save does not write an unsaved member change.
        """
        another = ACLAddressGroup.objects.create(name="another-v4")
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.address_group = another
        member.member = self.prefix1_v6
        member.save(update_fields={"address_group"})
        member.refresh_from_db()
        self.assertEqual(member.address_group, another)
        self.assertEqual(member.member, self.prefix1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_prefix").get()
        self.assertEqual(cached["_member_prefix"], self.prefix1.pk)

    def test_save_without_reference_fields_is_not_revalidated(self):
        """
        Test that a partial save naming no reference field skips validation.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        Prefix.objects.filter(pk=self.prefix1.pk).update(prefix=IPNetwork("2001:db8:1::/64"))
        member.member = self.ip_address1_v6
        member.comments = "note"
        for update_fields in ({"comments"}, iter(["comments"]), []):
            with self.subTest(update_fields=update_fields):
                member.save(update_fields=update_fields)
        member.refresh_from_db()
        self.assertEqual(member.comments, "note")
        self.assertEqual(member.member, self.prefix1)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_ipaddress").get()
        self.assertIsNone(cached["_member_ipaddress"])

    def test_complete_reference_save_moves_group_and_member_together(self):
        """
        Test that explicitly changing both references permits a cross-family move.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        member.address_group = self.ipv6_group
        member.member = self.ip_address1_v6

        member.save(update_fields={"address_group_id", "member_id"})

        member.refresh_from_db()
        self.assertEqual(member.address_group, self.ipv6_group)
        self.assertEqual(member.member, self.ip_address1_v6)
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_ipaddress", "_member_prefix").get()
        self.assertIsNone(cached["_member_prefix"])
        self.assertEqual(cached["_member_ipaddress"], self.ip_address1_v6.pk)
