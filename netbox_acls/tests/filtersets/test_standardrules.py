from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import RIR, Aggregate, IPAddress, IPRange, Prefix
from utilities.testing import ChangeLoggedFilterSetTests

from ...choices import ACLActionChoices, ACLFamilyChoices, ACLRuleActionChoices, ACLTypeChoices
from ...filtersets import ACLStandardRuleFilterSet
from ...models import AccessList, ACLStandardRule


class ACLStandardRuleFilterSetTestCase(TestCase, ChangeLoggedFilterSetTests):
    """FilterSet tests for ACLStandardRule."""

    queryset = ACLStandardRule.objects.all()
    filterset = ACLStandardRuleFilterSet
    # Reverse GenericRel accessors are not filterable fields, and the shared
    # test_missing_filters check skips GenericForeignKey and GenericRelation but not
    # GenericRel. These two are named differently from the filters that cover them,
    # source_ipaddress and source_iprange, so they surface as false positives.
    ignore_fields = ("source_ip_address", "source_ip_range")

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name="RIR 1", slug="rir-1")
        cls.aggregate = Aggregate.objects.create(prefix=IPNetwork("10.0.0.0/8"), rir=rir)
        cls.prefix = Prefix.objects.create(prefix=IPNetwork("10.1.0.0/16"))
        cls.ip_address = IPAddress.objects.create(address=IPNetwork("10.0.0.1/24"))
        cls.ip_range = IPRange.objects.create(
            start_address=IPNetwork("10.0.1.1/24"),
            end_address=IPNetwork("10.0.1.254/24"),
        )

        cls.access_list = AccessList.objects.create(
            name="teststandardacl",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # create() rather than bulk_create(), because save() is what runs
        # cache_related_source_object() to populate the _source_* shadow columns
        # that the source_prefix and friends filters actually query.
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=cls.prefix,
            description="permit the prefix",
            comments="reviewed quarterly",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=20,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=cls.ip_address,
            description="deny the address",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=30,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=cls.ip_range,
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=40,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="a standard remark",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=50,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=cls.aggregate,
            description="deny the aggregate",
        )

    def test_q(self):
        params = {"q": "a standard remark"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_matches_access_list_name(self):
        params = {"q": "teststandardacl"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_q_matches_comments(self):
        params = {"q": "reviewed"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_ignores_choice_values(self):
        """Two rules carry the Permit action, only one says permit in its text."""
        self.assertEqual(self.filterset({"q": "permit"}, self.queryset).qs.count(), 1)

    def test_q_matches_sequence_exactly(self):
        """A digit must not match every sequence that contains it."""
        self.assertEqual(self.filterset({"q": "10"}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({"q": "1"}, self.queryset).qs.count(), 0)
        self.assertEqual(self.filterset({"q": "0"}, self.queryset).qs.count(), 0)

    def test_q_ignores_blank_terms(self):
        """Ignoring a blank term means returning everything, not nothing."""
        self.assertEqual(self.filterset({"q": "   "}, self.queryset).qs.count(), 5)

    def test_access_list(self):
        params = {"access_list_id": [self.access_list.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {"access_list": [self.access_list.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_access_list_filter_accepts_any_acl_type(self):
        """
        The standard rule filters accept an extended access list while the extended rule
        filters reject a standard one. Pinned so the asymmetry cannot change unnoticed.
        """
        extended_acl = AccessList.objects.create(
            name="anextendedacl",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        filterset = self.filterset({}, self.queryset)
        self.assertIn(extended_acl, filterset.filters["access_list"].queryset)
        self.assertIn(extended_acl, filterset.filters["access_list_id"].queryset)

    def test_sequence(self):
        params = {"sequence": [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_remark(self):
        params = {"remark": ["a standard remark"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {"description": ["permit the prefix", "deny the address"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_source_type(self):
        params = {"source_type": "ipam.prefix"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_type": "ipam.iprange"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_id_is_type_agnostic(self):
        """source_id filters the raw generic FK column, so it needs source_type to narrow."""
        params = {"source_id": [self.prefix.pk], "source_type": "ipam.prefix"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_prefix(self):
        params = {"source_prefix_id": [self.prefix.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_prefix": [self.prefix.prefix]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_ipaddress(self):
        params = {"source_ipaddress_id": [self.ip_address.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ipaddress": [self.ip_address.address]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_iprange(self):
        params = {"source_iprange_id": [self.ip_range.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_iprange": [self.ip_range.start_address]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_aggregate(self):
        params = {"source_aggregate_id": [self.aggregate.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_aggregate": [self.aggregate.prefix]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    # comments is a TextField, which django-filter maps to a single-valued CharFilter
    # matching exactly, unlike the CharField-backed description above.

    def test_comments(self):
        params = {"comments": "reviewed quarterly"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    # action is a single-valued ChoiceFilter, so assert one value at a time.

    def test_action(self):
        params = {"action": ACLRuleActionChoices.ACTION_PERMIT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"action": ACLRuleActionChoices.ACTION_REMARK}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
