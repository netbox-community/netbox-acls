from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLExtendedRule, ACLStandardRule
from .base import BaseTestCase


class TestACLRuleGenericRelations(BaseTestCase):
    """
    Test the generic relations contributed to the ipam models.

    Nothing reads them yet, so without these tests a wrong content type field or
    query name goes unnoticed until a view is built on top of them.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Extend BaseTestCase's setUpTestData() with one rule per source type, each
        extended rule taking a different object as its destination.
        """
        super().setUpTestData()

        cls.standard_acl = AccessList.objects.create(
            name="STANDARD_ACL",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        cls.extended_acl = AccessList.objects.create(
            name="EXTENDED_ACL",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # Keyed by the related_query_name segment the relation uses for that model.
        cls.sources = {
            "aggregate": cls.aggregate1,
            "ip_address": cls.ip_address1,
            "ip_range": cls.ip_range1,
            "prefix": cls.prefix1,
        }
        cls.destinations = {
            "aggregate": cls.aggregate2,
            "ip_address": cls.ip_address2,
            "ip_range": cls.ip_range2,
            "prefix": cls.prefix2,
        }

        cls.standard_rules = {}
        cls.extended_rules = {}
        for index, name in enumerate(cls.sources):
            sequence = (index + 1) * 10
            # create() rather than bulk_create(), because save() is what populates
            # the shadow columns.
            cls.standard_rules[name] = ACLStandardRule.objects.create(
                access_list=cls.standard_acl,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=cls.sources[name],
            )
            cls.extended_rules[name] = ACLExtendedRule.objects.create(
                access_list=cls.extended_acl,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=cls.sources[name],
                destination=cls.destinations[name],
            )

    def test_standard_rule_reachable_from_its_source(self):
        """Test that a standard rule is listed on the ipam object it sources."""
        for name, source in self.sources.items():
            with self.subTest(source=name):
                self.assertEqual(
                    list(source.accesslist_standard_rule_sources.all()),
                    [self.standard_rules[name]],
                )

    def test_extended_rule_reachable_from_its_source(self):
        """Test that an extended rule is listed on the ipam object it sources."""
        for name, source in self.sources.items():
            with self.subTest(source=name):
                self.assertEqual(
                    list(source.accesslist_extended_rule_sources.all()),
                    [self.extended_rules[name]],
                )

    def test_extended_rule_reachable_from_its_destination(self):
        """Test that an extended rule is listed on the ipam object it targets."""
        for name, destination in self.destinations.items():
            with self.subTest(destination=name):
                self.assertEqual(
                    list(destination.accesslist_extended_rule_destinations.all()),
                    [self.extended_rules[name]],
                )

    def test_rules_filter_by_source_query_name(self):
        """Test that the reverse query name filters rules by their source object."""
        for name, source in self.sources.items():
            with self.subTest(source=name):
                self.assertEqual(
                    list(ACLStandardRule.objects.filter(**{f"source_{name}": source})),
                    [self.standard_rules[name]],
                )
                self.assertEqual(
                    list(ACLExtendedRule.objects.filter(**{f"source_{name}": source})),
                    [self.extended_rules[name]],
                )

    def test_rules_filter_by_destination_query_name(self):
        """Test that the reverse query name filters rules by their destination object."""
        for name, destination in self.destinations.items():
            with self.subTest(destination=name):
                self.assertEqual(
                    list(ACLExtendedRule.objects.filter(**{f"destination_{name}": destination})),
                    [self.extended_rules[name]],
                )

    def test_source_and_destination_relations_stay_apart(self):
        """Test that a source object reports no destinations, and the reverse."""
        for name in self.sources:
            with self.subTest(target=name):
                self.assertEqual(self.sources[name].accesslist_extended_rule_destinations.count(), 0)
                self.assertEqual(self.destinations[name].accesslist_extended_rule_sources.count(), 0)
