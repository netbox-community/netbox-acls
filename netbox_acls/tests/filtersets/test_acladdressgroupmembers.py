from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import RIR, Aggregate, IPAddress, IPRange, Prefix
from utilities.testing import ChangeLoggedFilterSetTestMixin

from ...filtersets import ACLAddressGroupMemberFilterSet
from ...models import ACLAddressGroup, ACLAddressGroupMember


class ACLAddressGroupMemberFilterSetTestCase(TestCase, ChangeLoggedFilterSetTestMixin):
    """FilterSet tests for ACLAddressGroupMember."""

    queryset = ACLAddressGroupMember.objects.all()
    filterset = ACLAddressGroupMemberFilterSet
    # Reverse GenericRel accessors from the IPAM models are not filterable fields.
    ignore_fields = ("member_ip_address", "member_ip_range")

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
        other_prefix = Prefix.objects.create(prefix=IPNetwork("10.2.0.0/16"))
        third_prefix = Prefix.objects.create(prefix=IPNetwork("10.3.0.0/16"))

        cls.address_group = ACLAddressGroup.objects.create(name="trusted")
        other_group = ACLAddressGroup.objects.create(name="other")
        third_group = ACLAddressGroup.objects.create(name="third")

        ACLAddressGroupMember.objects.create(
            address_group=cls.address_group,
            member=cls.prefix,
            comments="reviewed quarterly",
        )
        ACLAddressGroupMember.objects.create(
            address_group=other_group,
            member=other_prefix,
        )
        ACLAddressGroupMember.objects.create(
            address_group=other_group,
            member=cls.ip_address,
        )
        ACLAddressGroupMember.objects.create(
            address_group=third_group,
            member=third_prefix,
        )
        ACLAddressGroupMember.objects.create(
            address_group=third_group,
            member=cls.ip_range,
        )
        ACLAddressGroupMember.objects.create(
            address_group=third_group,
            member=cls.aggregate,
        )

    def test_q(self):
        params = {"q": "trusted"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_matches_comments(self):
        params = {"q": "reviewed"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_ignores_blank_terms(self):
        """Ignoring a blank term means returning everything, not nothing."""
        self.assertEqual(self.filterset({"q": "   "}, self.queryset).qs.count(), 6)

    def test_address_group(self):
        params = {"address_group_id": [self.address_group.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"address_group": [self.address_group.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_member_type(self):
        params = {"member_type": ["ipam.prefix"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"member_type": ["ipam.prefix", "ipam.iprange"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_member_type_id(self):
        params = {"member_type_id": [ContentType.objects.get_for_model(Prefix).pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {
            "member_type_id": [
                ContentType.objects.get_for_model(IPAddress).pk,
                ContentType.objects.get_for_model(Aggregate).pk,
            ],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_member_type_id_outside_whitelist_matches_nothing(self):
        """A type that cannot be a member matches nothing rather than erroring."""
        params = {"member_type_id": [ContentType.objects.get_for_model(ACLAddressGroup).pk]}
        filterset = self.filterset(params, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 0)

    def test_member_id_is_type_agnostic(self):
        """member_id filters the raw generic FK column, whatever the member type."""
        params = {"member_id": [self.prefix.pk], "member_type": ["ipam.prefix"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_member_aggregate(self):
        params = {"member_aggregate_id": [self.aggregate.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"member_aggregate": [self.aggregate.prefix]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_member_ipaddress(self):
        params = {"member_ipaddress_id": [self.ip_address.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"member_ipaddress": [self.ip_address.address]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_member_iprange(self):
        params = {"member_iprange_id": [self.ip_range.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"member_iprange": [self.ip_range.start_address]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_member_prefix(self):
        params = {"member_prefix_id": [self.prefix.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"member_prefix": [self.prefix.prefix]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_comments(self):
        params = {"comments": "reviewed quarterly"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
