from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import RIR, Aggregate, IPAddress, IPRange, Prefix
from utilities.testing import ChangeLoggedFilterSetTestMixin

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ...filtersets import ACLExtendedRuleFilterSet
from ...models import AccessList, ACLExtendedRule
from ...utils import normalize_port_ranges


class ACLExtendedRuleFilterSetTestCase(TestCase, ChangeLoggedFilterSetTestMixin):
    """FilterSet tests for ACLExtendedRule."""

    queryset = ACLExtendedRule.objects.all()
    filterset = ACLExtendedRuleFilterSet
    # Reverse GenericRel accessors are not filterable fields, and the shared
    # test_missing_filters check skips GenericForeignKey and GenericRelation but not
    # GenericRel. These four are named differently from the filters that cover them,
    # source_ipaddress, source_iprange, destination_ipaddress and destination_iprange.
    # The port range columns are covered by the source_port and destination_port
    # filters, which ask whether any stored range contains a given port. That is the
    # useful question, so there is deliberately no filter named after the raw column.
    ignore_fields = (
        "source_ip_address",
        "source_ip_range",
        "destination_ip_address",
        "destination_ip_range",
        "source_port_ranges",
        "destination_port_ranges",
    )

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name="RIR 1", slug="rir-1")
        cls.aggregate = Aggregate.objects.create(prefix=IPNetwork("10.0.0.0/8"), rir=rir)
        cls.source_prefix = Prefix.objects.create(prefix=IPNetwork("10.1.0.0/16"))
        cls.destination_prefix = Prefix.objects.create(prefix=IPNetwork("10.2.0.0/16"))
        cls.ip_address = IPAddress.objects.create(address=IPNetwork("10.0.0.1/24"))
        cls.ip_range = IPRange.objects.create(
            start_address=IPNetwork("10.0.1.1/24"),
            end_address=IPNetwork("10.0.1.254/24"),
        )

        cls.access_list = AccessList.objects.create(
            name="testextendedacl",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # Port ranges are stored half-open. normalize_port_ranges turns the inclusive
        # form the UI shows into what the column holds, so 80 to 80 becomes [80, 81).
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            source=cls.source_prefix,
            destination=cls.destination_prefix,
            source_port_ranges=normalize_port_ranges([NumericRange(1024, 2048, bounds="[]")]),
            destination_port_ranges=normalize_port_ranges([NumericRange(80, 80, bounds="[]")]),
            description="permit web",
            comments="reviewed quarterly",
            log_matches=True,
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=20,
            action=ACLRuleActionChoices.ACTION_DENY,
            protocol=ACLProtocolChoices.PROTOCOL_UDP,
            source=cls.ip_address,
            destination=cls.ip_range,
            destination_port_ranges=normalize_port_ranges([NumericRange(53, 53, bounds="[]")]),
            description="deny dns",
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=30,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            source=cls.aggregate,
            destination=cls.ip_address,
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=40,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="an extended remark",
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=50,
            action=ACLRuleActionChoices.ACTION_DENY,
            protocol=ACLProtocolChoices.PROTOCOL_IP,
            source=cls.ip_range,
            destination=cls.aggregate,
            description="deny the range",
        )

    def test_q(self):
        params = {"q": "an extended remark"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_ignores_choice_values(self):
        """Zero is correct here. The protocol has its own filter."""
        params = {"q": ACLProtocolChoices.PROTOCOL_ICMP}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_q_matches_sequence_exactly(self):
        """A digit must not match every sequence that contains it."""
        self.assertEqual(self.filterset({"q": "10"}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({"q": "1"}, self.queryset).qs.count(), 0)
        self.assertEqual(self.filterset({"q": "0"}, self.queryset).qs.count(), 0)

    def test_q_matches_comments(self):
        params = {"q": "reviewed"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_ignores_blank_terms(self):
        """Ignoring a blank term means returning everything, not nothing."""
        self.assertEqual(self.filterset({"q": "   "}, self.queryset).qs.count(), 5)

    def test_access_list(self):
        params = {"access_list_id": [self.access_list.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {"access_list": [self.access_list.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_access_list_filter_is_limited_to_extended(self):
        """
        The extended rule filters reject a standard access list while the standard rule
        filters accept any type. Pinned so the asymmetry cannot change unnoticed.
        """
        standard_acl = AccessList.objects.create(
            name="astandardacl",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        filterset = self.filterset({}, self.queryset)
        self.assertNotIn(standard_acl, filterset.filters["access_list"].queryset)
        self.assertNotIn(standard_acl, filterset.filters["access_list_id"].queryset)

    def test_sequence(self):
        params = {"sequence": [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_remark(self):
        params = {"remark": ["an extended remark"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {"description": ["permit web"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_type(self):
        params = {"source_type": "ipam.prefix"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_type": "ipam.aggregate"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_type": "ipam.iprange"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_id_is_type_agnostic(self):
        """source_id filters the raw generic FK column, so it needs source_type to narrow."""
        params = {"source_id": [self.source_prefix.pk], "source_type": "ipam.prefix"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_prefix(self):
        params = {"source_prefix_id": [self.source_prefix.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_prefix": [self.source_prefix.prefix]}
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

    def test_destination_type(self):
        params = {"destination_type": "ipam.prefix"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_type": "ipam.iprange"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_type": "ipam.aggregate"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_destination_id_is_type_agnostic(self):
        """destination_id filters the raw generic FK column, so it needs destination_type."""
        params = {
            "destination_id": [self.destination_prefix.pk],
            "destination_type": "ipam.prefix",
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_destination_prefix(self):
        params = {"destination_prefix_id": [self.destination_prefix.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_prefix": [self.destination_prefix.prefix]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_destination_iprange(self):
        params = {"destination_iprange_id": [self.ip_range.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_iprange": [self.ip_range.start_address]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_destination_ipaddress(self):
        params = {"destination_ipaddress_id": [self.ip_address.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_ipaddress": [self.ip_address.address]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_destination_aggregate(self):
        params = {"destination_aggregate_id": [self.aggregate.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_aggregate": [self.aggregate.prefix]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    # comments is a TextField, which django-filter maps to a single-valued CharFilter
    # matching exactly, unlike the CharField-backed description above.

    def test_comments(self):
        params = {"comments": "reviewed quarterly"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_port(self):
        params = {"source_port": 1500}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_port": 3000}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_destination_port(self):
        params = {"destination_port": 80}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_port": 53}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_destination_port_excludes_half_open_upper_bound(self):
        """81 is the stored exclusive upper bound of an inclusive 80 to 80 range."""
        params = {"destination_port": 81}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    # action and protocol are single-valued ChoiceFilters, so assert one value at a time.

    def test_action(self):
        params = {"action": ACLRuleActionChoices.ACTION_PERMIT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"action": ACLRuleActionChoices.ACTION_DENY}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_protocol(self):
        params = {"protocol": ACLProtocolChoices.PROTOCOL_TCP}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"protocol": ACLProtocolChoices.PROTOCOL_UDP}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_log_matches(self):
        params = {"log_matches": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_log_options(self):
        params = {"log_options": ["syslog"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
