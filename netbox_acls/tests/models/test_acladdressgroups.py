from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from ipam.models import Prefix

from ...choices import ACLAddressFamilyChoices, ACLFamilyChoices, ACLRuleActionChoices, ACLTypeChoices
from ...models import AccessList, ACLAddressGroup, ACLAddressGroupMember, ACLExtendedRule, ACLStandardRule
from ...utils import infer_family_from_object
from .base import BaseTestCase


class TestACLAddressGroup(BaseTestCase):
    """
    Test ACLAddressGroup model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Extend BaseTestCase's setUpTestData() to create additional data for testing.
        """
        super().setUpTestData()

        cls.group = ACLAddressGroup.objects.create(name="servers-v4")
        cls.standard_acl = AccessList.objects.create(
            name="STANDARD_ACL",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )
        cls.extended_acl = AccessList.objects.create(
            name="EXTENDED_ACL",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )

    def test_name_is_globally_unique_in_full_clean(self):
        """
        Test that an address group name already in use fails validation.
        """
        group = ACLAddressGroup(name=self.group.name, family=ACLAddressFamilyChoices.FAMILY_IPV6)
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_name_is_globally_unique_in_save(self):
        """
        Test that the database rejects an address group name already in use.
        """
        group = ACLAddressGroup(name=self.group.name, family=ACLAddressFamilyChoices.FAMILY_IPV6)
        with self.assertRaises(IntegrityError), transaction.atomic():
            group.save()

    def test_group_family_is_never_dual(self):
        """
        Test that the dual family is not valid for an address group.
        """
        group = ACLAddressGroup(name="dual", family=ACLFamilyChoices.FAMILY_DUAL)
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_empty_unused_group_may_change_family(self):
        """
        Test that an empty, unused address group may change its family.
        """
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        self.group.full_clean()
        self.group.save()
        self.group.refresh_from_db()
        self.assertEqual(self.group.family, ACLAddressFamilyChoices.FAMILY_IPV6)

    def test_member_blocks_family_change_in_clean(self):
        """
        Test that a member blocks a family change in clean().
        """
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            self.group.full_clean()

    def test_member_blocks_family_change_in_save(self):
        """
        Test that a member blocks a family change in save().
        """
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            self.group.save()

    def test_standard_rule_source_blocks_family_change_in_clean(self):
        """
        Test that a standard rule source blocks a family change in clean(), even without members.
        """
        ACLStandardRule.objects.create(
            access_list=self.standard_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            self.group.full_clean()

    def test_standard_rule_source_blocks_family_change_in_save(self):
        """
        Test that a standard rule source blocks a family change in save(), even without members.
        """
        ACLStandardRule.objects.create(
            access_list=self.standard_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            self.group.save()

    def test_extended_rule_source_blocks_family_change_in_clean(self):
        """
        Test that an extended rule source blocks a family change in clean(), even without members.
        """
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            self.group.full_clean()

    def test_extended_rule_source_blocks_family_change_in_save(self):
        """
        Test that an extended rule source blocks a family change in save(), even without members.
        """
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            self.group.save()

    def test_extended_rule_destination_blocks_family_change_in_clean(self):
        """
        Test that an extended rule destination blocks a family change in clean(), even without members.
        """
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            destination=self.group,
        )
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            self.group.full_clean()

    def test_extended_rule_destination_blocks_family_change_in_save(self):
        """
        Test that an extended rule destination blocks a family change in save(), even without members.
        """
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            destination=self.group,
        )
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            self.group.save()

    def test_deleting_unused_group_cascades_members_not_ipam_objects(self):
        """
        Test that deleting a group removes its memberships but not the IPAM objects.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        pk = member.pk
        self.group.delete()
        self.assertFalse(ACLAddressGroupMember.objects.filter(pk=pk).exists())
        self.assertTrue(Prefix.objects.filter(pk=self.prefix1.pk).exists())

    def test_standard_rule_source_protects_group_from_deletion(self):
        """
        Test that a group used as a standard rule source cannot be deleted.
        """
        ACLStandardRule.objects.create(
            access_list=self.standard_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        with self.assertRaises(ProtectedError):
            self.group.delete()

    def test_extended_rule_source_protects_group_from_deletion(self):
        """
        Test that a group used as an extended rule source cannot be deleted.
        """
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        with self.assertRaises(ProtectedError):
            self.group.delete()

    def test_extended_rule_destination_protects_group_from_deletion(self):
        """
        Test that a group used as an extended rule destination cannot be deleted.
        """
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            destination=self.group,
        )
        with self.assertRaises(ProtectedError):
            self.group.delete()

    def test_last_member_may_be_removed_from_referenced_group(self):
        """
        Test that a referenced group may lose its last member.
        """
        member = ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        ACLStandardRule.objects.create(
            access_list=self.standard_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        member.delete()
        self.assertFalse(self.group.acladdressgroupmembers.exists())
        self.assertTrue(self.group.accesslist_standard_rule_sources.exists())

    def test_family_inference_accepts_group_strings_and_ipam_numbers(self):
        """
        Test that family inference reads a group's family and an IPAM object's version.
        """
        self.assertEqual(infer_family_from_object(self.group), ACLFamilyChoices.FAMILY_IPV4)
        self.assertEqual(infer_family_from_object(self.prefix1), ACLFamilyChoices.FAMILY_IPV4)
        ipv6 = ACLAddressGroup.objects.create(name="v6", family=ACLAddressFamilyChoices.FAMILY_IPV6)
        self.assertEqual(infer_family_from_object(ipv6), ACLFamilyChoices.FAMILY_IPV6)

    def test_group_clone_does_not_copy_members(self):
        """
        Test that cloning a group copies its family but not its members.
        """
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        attrs = self.group.clone()
        self.assertEqual(attrs["family"], self.group.family)
        self.assertNotIn("acladdressgroupmembers", attrs)

    def test_family_guard_reads_member_past_a_prefetched_relation_in_clean(self):
        """
        Test that clean() sees a member added after the members were prefetched.
        """
        stale = ACLAddressGroup.objects.prefetch_related("acladdressgroupmembers").get(pk=self.group.pk)
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        stale.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            stale.full_clean()

    def test_family_guard_reads_member_past_a_prefetched_relation_in_save(self):
        """
        Test that save() sees a member added after the members were prefetched.
        """
        stale = ACLAddressGroup.objects.prefetch_related("acladdressgroupmembers").get(pk=self.group.pk)
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        stale.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            stale.save()

    def test_family_guard_reads_standard_rule_source_past_a_prefetched_relation_in_clean(self):
        """
        Test that clean() sees a standard rule source added after the relation was prefetched.
        """
        stale = ACLAddressGroup.objects.prefetch_related("accesslist_standard_rule_sources").get(pk=self.group.pk)
        ACLStandardRule.objects.create(
            access_list=self.standard_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        stale.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            stale.full_clean()

    def test_family_guard_reads_standard_rule_source_past_a_prefetched_relation_in_save(self):
        """
        Test that save() sees a standard rule source added after the relation was prefetched.
        """
        stale = ACLAddressGroup.objects.prefetch_related("accesslist_standard_rule_sources").get(pk=self.group.pk)
        ACLStandardRule.objects.create(
            access_list=self.standard_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        stale.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            stale.save()

    def test_family_guard_reads_extended_rule_source_past_a_prefetched_relation_in_clean(self):
        """
        Test that clean() sees an extended rule source added after the relation was prefetched.
        """
        stale = ACLAddressGroup.objects.prefetch_related("accesslist_extended_rule_sources").get(pk=self.group.pk)
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        stale.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            stale.full_clean()

    def test_family_guard_reads_extended_rule_source_past_a_prefetched_relation_in_save(self):
        """
        Test that save() sees an extended rule source added after the relation was prefetched.
        """
        stale = ACLAddressGroup.objects.prefetch_related("accesslist_extended_rule_sources").get(pk=self.group.pk)
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.group,
        )
        stale.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            stale.save()

    def test_family_guard_reads_extended_rule_destination_past_a_prefetched_relation_in_clean(self):
        """
        Test that clean() sees an extended rule destination added after the relation was prefetched.
        """
        stale = ACLAddressGroup.objects.prefetch_related("accesslist_extended_rule_destinations").get(pk=self.group.pk)
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            destination=self.group,
        )
        stale.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            stale.full_clean()

    def test_family_guard_reads_extended_rule_destination_past_a_prefetched_relation_in_save(self):
        """
        Test that save() sees an extended rule destination added after the relation was prefetched.
        """
        stale = ACLAddressGroup.objects.prefetch_related("accesslist_extended_rule_destinations").get(pk=self.group.pk)
        ACLExtendedRule.objects.create(
            access_list=self.extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            destination=self.group,
        )
        stale.family = ACLAddressFamilyChoices.FAMILY_IPV6
        with self.assertRaises(ValidationError):
            stale.save()

    def test_metadata_only_save_does_not_write_or_validate_a_dirty_family(self):
        """
        Test that update_fields excluding a family change skips the family guard even when the group is in use.
        """
        ACLAddressGroupMember.objects.create(address_group=self.group, member=self.prefix1)
        self.group.family = ACLAddressFamilyChoices.FAMILY_IPV6
        self.group.description = "Updated description"

        self.group.save(update_fields=iter(["description"]))

        self.group.refresh_from_db()
        self.assertEqual(self.group.family, ACLAddressFamilyChoices.FAMILY_IPV4)
        self.assertEqual(self.group.description, "Updated description")
