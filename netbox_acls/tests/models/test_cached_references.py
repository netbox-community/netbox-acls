from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase

from ...models import ACLAddressGroupMember, ACLExtendedRule, ACLStandardRule


class TestCachedGenericReference(SimpleTestCase):
    """
    Test the shadow columns cache_related_objects() maintains.
    """

    def test_member_fills_only_its_aggregate_shadow(self):
        """
        Test that an aggregate member copies its id into the aggregate shadow alone.
        """
        member = ACLAddressGroupMember(member_type=ContentType(id=1, app_label="ipam", model="aggregate"), member_id=42)
        member.cache_related_objects("member")
        self.assertEqual(getattr(member, "_member_aggregate_id"), 42)
        self.assertIsNone(getattr(member, "_member_ipaddress_id"))
        self.assertIsNone(getattr(member, "_member_iprange_id"))
        self.assertIsNone(getattr(member, "_member_prefix_id"))

    def test_member_fills_only_its_ip_address_shadow(self):
        """
        Test that an IP address member copies its id into the IP address shadow alone.
        """
        member = ACLAddressGroupMember(member_type=ContentType(id=1, app_label="ipam", model="ipaddress"), member_id=42)
        member.cache_related_objects("member")
        self.assertIsNone(getattr(member, "_member_aggregate_id"))
        self.assertEqual(getattr(member, "_member_ipaddress_id"), 42)
        self.assertIsNone(getattr(member, "_member_iprange_id"))
        self.assertIsNone(getattr(member, "_member_prefix_id"))

    def test_member_fills_only_its_ip_range_shadow(self):
        """
        Test that an IP range member copies its id into the IP range shadow alone.
        """
        member = ACLAddressGroupMember(member_type=ContentType(id=1, app_label="ipam", model="iprange"), member_id=42)
        member.cache_related_objects("member")
        self.assertIsNone(getattr(member, "_member_aggregate_id"))
        self.assertIsNone(getattr(member, "_member_ipaddress_id"))
        self.assertEqual(getattr(member, "_member_iprange_id"), 42)
        self.assertIsNone(getattr(member, "_member_prefix_id"))

    def test_member_fills_only_its_prefix_shadow(self):
        """
        Test that a prefix member copies its id into the prefix shadow alone.
        """
        member = ACLAddressGroupMember(member_type=ContentType(id=1, app_label="ipam", model="prefix"), member_id=42)
        member.cache_related_objects("member")
        self.assertIsNone(getattr(member, "_member_aggregate_id"))
        self.assertIsNone(getattr(member, "_member_ipaddress_id"))
        self.assertIsNone(getattr(member, "_member_iprange_id"))
        self.assertEqual(getattr(member, "_member_prefix_id"), 42)

    def test_standard_rule_source_fills_only_its_address_group_shadow(self):
        """
        Test that an address group source copies its id into the address group shadow alone.
        """
        rule = ACLStandardRule(
            source_type=ContentType(id=1, app_label="netbox_acls", model="acladdressgroup"),
            source_id=42,
        )
        rule.cache_related_objects("source")
        self.assertEqual(getattr(rule, "_source_acladdressgroup_id"), 42)
        self.assertIsNone(getattr(rule, "_source_aggregate_id"))
        self.assertIsNone(getattr(rule, "_source_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_source_iprange_id"))
        self.assertIsNone(getattr(rule, "_source_prefix_id"))

    def test_standard_rule_source_fills_only_its_aggregate_shadow(self):
        """
        Test that an aggregate source copies its id into the aggregate shadow alone.
        """
        rule = ACLStandardRule(source_type=ContentType(id=1, app_label="ipam", model="aggregate"), source_id=42)
        rule.cache_related_objects("source")
        self.assertIsNone(getattr(rule, "_source_acladdressgroup_id"))
        self.assertEqual(getattr(rule, "_source_aggregate_id"), 42)
        self.assertIsNone(getattr(rule, "_source_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_source_iprange_id"))
        self.assertIsNone(getattr(rule, "_source_prefix_id"))

    def test_standard_rule_source_fills_only_its_ip_address_shadow(self):
        """
        Test that an IP address source copies its id into the IP address shadow alone.
        """
        rule = ACLStandardRule(source_type=ContentType(id=1, app_label="ipam", model="ipaddress"), source_id=42)
        rule.cache_related_objects("source")
        self.assertIsNone(getattr(rule, "_source_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_source_aggregate_id"))
        self.assertEqual(getattr(rule, "_source_ipaddress_id"), 42)
        self.assertIsNone(getattr(rule, "_source_iprange_id"))
        self.assertIsNone(getattr(rule, "_source_prefix_id"))

    def test_standard_rule_source_fills_only_its_ip_range_shadow(self):
        """
        Test that an IP range source copies its id into the IP range shadow alone.
        """
        rule = ACLStandardRule(source_type=ContentType(id=1, app_label="ipam", model="iprange"), source_id=42)
        rule.cache_related_objects("source")
        self.assertIsNone(getattr(rule, "_source_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_source_aggregate_id"))
        self.assertIsNone(getattr(rule, "_source_ipaddress_id"))
        self.assertEqual(getattr(rule, "_source_iprange_id"), 42)
        self.assertIsNone(getattr(rule, "_source_prefix_id"))

    def test_standard_rule_source_fills_only_its_prefix_shadow(self):
        """
        Test that a prefix source copies its id into the prefix shadow alone.
        """
        rule = ACLStandardRule(source_type=ContentType(id=1, app_label="ipam", model="prefix"), source_id=42)
        rule.cache_related_objects("source")
        self.assertIsNone(getattr(rule, "_source_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_source_aggregate_id"))
        self.assertIsNone(getattr(rule, "_source_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_source_iprange_id"))
        self.assertEqual(getattr(rule, "_source_prefix_id"), 42)

    def test_extended_rule_source_fills_only_its_address_group_shadow(self):
        """
        Test that an address group source copies its id into the address group shadow alone.
        """
        rule = ACLExtendedRule(
            source_type=ContentType(id=1, app_label="netbox_acls", model="acladdressgroup"),
            source_id=42,
        )
        rule.cache_related_objects("source")
        self.assertEqual(getattr(rule, "_source_acladdressgroup_id"), 42)
        self.assertIsNone(getattr(rule, "_source_aggregate_id"))
        self.assertIsNone(getattr(rule, "_source_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_source_iprange_id"))
        self.assertIsNone(getattr(rule, "_source_prefix_id"))

    def test_extended_rule_source_fills_only_its_aggregate_shadow(self):
        """
        Test that an aggregate source copies its id into the aggregate shadow alone.
        """
        rule = ACLExtendedRule(source_type=ContentType(id=1, app_label="ipam", model="aggregate"), source_id=42)
        rule.cache_related_objects("source")
        self.assertIsNone(getattr(rule, "_source_acladdressgroup_id"))
        self.assertEqual(getattr(rule, "_source_aggregate_id"), 42)
        self.assertIsNone(getattr(rule, "_source_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_source_iprange_id"))
        self.assertIsNone(getattr(rule, "_source_prefix_id"))

    def test_extended_rule_source_fills_only_its_ip_address_shadow(self):
        """
        Test that an IP address source copies its id into the IP address shadow alone.
        """
        rule = ACLExtendedRule(source_type=ContentType(id=1, app_label="ipam", model="ipaddress"), source_id=42)
        rule.cache_related_objects("source")
        self.assertIsNone(getattr(rule, "_source_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_source_aggregate_id"))
        self.assertEqual(getattr(rule, "_source_ipaddress_id"), 42)
        self.assertIsNone(getattr(rule, "_source_iprange_id"))
        self.assertIsNone(getattr(rule, "_source_prefix_id"))

    def test_extended_rule_source_fills_only_its_ip_range_shadow(self):
        """
        Test that an IP range source copies its id into the IP range shadow alone.
        """
        rule = ACLExtendedRule(source_type=ContentType(id=1, app_label="ipam", model="iprange"), source_id=42)
        rule.cache_related_objects("source")
        self.assertIsNone(getattr(rule, "_source_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_source_aggregate_id"))
        self.assertIsNone(getattr(rule, "_source_ipaddress_id"))
        self.assertEqual(getattr(rule, "_source_iprange_id"), 42)
        self.assertIsNone(getattr(rule, "_source_prefix_id"))

    def test_extended_rule_source_fills_only_its_prefix_shadow(self):
        """
        Test that a prefix source copies its id into the prefix shadow alone.
        """
        rule = ACLExtendedRule(source_type=ContentType(id=1, app_label="ipam", model="prefix"), source_id=42)
        rule.cache_related_objects("source")
        self.assertIsNone(getattr(rule, "_source_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_source_aggregate_id"))
        self.assertIsNone(getattr(rule, "_source_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_source_iprange_id"))
        self.assertEqual(getattr(rule, "_source_prefix_id"), 42)

    def test_extended_rule_destination_fills_only_its_address_group_shadow(self):
        """
        Test that an address group destination copies its id into the address group shadow alone.
        """
        rule = ACLExtendedRule(
            destination_type=ContentType(id=1, app_label="netbox_acls", model="acladdressgroup"),
            destination_id=42,
        )
        rule.cache_related_objects("destination")
        self.assertEqual(getattr(rule, "_destination_acladdressgroup_id"), 42)
        self.assertIsNone(getattr(rule, "_destination_aggregate_id"))
        self.assertIsNone(getattr(rule, "_destination_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_destination_iprange_id"))
        self.assertIsNone(getattr(rule, "_destination_prefix_id"))

    def test_extended_rule_destination_fills_only_its_aggregate_shadow(self):
        """
        Test that an aggregate destination copies its id into the aggregate shadow alone.
        """
        rule = ACLExtendedRule(
            destination_type=ContentType(id=1, app_label="ipam", model="aggregate"),
            destination_id=42,
        )
        rule.cache_related_objects("destination")
        self.assertIsNone(getattr(rule, "_destination_acladdressgroup_id"))
        self.assertEqual(getattr(rule, "_destination_aggregate_id"), 42)
        self.assertIsNone(getattr(rule, "_destination_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_destination_iprange_id"))
        self.assertIsNone(getattr(rule, "_destination_prefix_id"))

    def test_extended_rule_destination_fills_only_its_ip_address_shadow(self):
        """
        Test that an IP address destination copies its id into the IP address shadow alone.
        """
        rule = ACLExtendedRule(
            destination_type=ContentType(id=1, app_label="ipam", model="ipaddress"),
            destination_id=42,
        )
        rule.cache_related_objects("destination")
        self.assertIsNone(getattr(rule, "_destination_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_destination_aggregate_id"))
        self.assertEqual(getattr(rule, "_destination_ipaddress_id"), 42)
        self.assertIsNone(getattr(rule, "_destination_iprange_id"))
        self.assertIsNone(getattr(rule, "_destination_prefix_id"))

    def test_extended_rule_destination_fills_only_its_ip_range_shadow(self):
        """
        Test that an IP range destination copies its id into the IP range shadow alone.
        """
        rule = ACLExtendedRule(destination_type=ContentType(id=1, app_label="ipam", model="iprange"), destination_id=42)
        rule.cache_related_objects("destination")
        self.assertIsNone(getattr(rule, "_destination_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_destination_aggregate_id"))
        self.assertIsNone(getattr(rule, "_destination_ipaddress_id"))
        self.assertEqual(getattr(rule, "_destination_iprange_id"), 42)
        self.assertIsNone(getattr(rule, "_destination_prefix_id"))

    def test_extended_rule_destination_fills_only_its_prefix_shadow(self):
        """
        Test that a prefix destination copies its id into the prefix shadow alone.
        """
        rule = ACLExtendedRule(destination_type=ContentType(id=1, app_label="ipam", model="prefix"), destination_id=42)
        rule.cache_related_objects("destination")
        self.assertIsNone(getattr(rule, "_destination_acladdressgroup_id"))
        self.assertIsNone(getattr(rule, "_destination_aggregate_id"))
        self.assertIsNone(getattr(rule, "_destination_ipaddress_id"))
        self.assertIsNone(getattr(rule, "_destination_iprange_id"))
        self.assertEqual(getattr(rule, "_destination_prefix_id"), 42)

    def test_clearing_a_role_clears_only_that_roles_shadows(self):
        """
        Test that clearing an optional criterion leaves the opposite end untouched.
        """
        instance = ACLExtendedRule()
        setattr(instance, "_source_prefix_id", 10)
        setattr(instance, "_destination_prefix_id", 20)

        instance.cache_related_objects("source")

        self.assertIsNone(getattr(instance, "_source_prefix_id"))
        self.assertEqual(getattr(instance, "_destination_prefix_id"), 20)

    def test_content_type_matching_includes_the_app_label(self):
        """
        Test that a different app's model of the same name cannot select an IPAM shadow.
        """
        instance = ACLStandardRule(
            source_type=ContentType(id=1, app_label="other_app", model="prefix"),
            source_id=42,
        )
        setattr(instance, "_source_prefix_id", 99)

        instance.cache_related_objects("source")

        self.assertIsNone(getattr(instance, "_source_prefix_id"))
