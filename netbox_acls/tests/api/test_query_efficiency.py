"""Tests that list endpoints resolve their relations in a bounded number of queries."""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from dcim.choices import InterfaceTypeChoices
from utilities.testing import APITestCase, create_test_device, create_test_virtualmachine

from ...choices import (
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule
from ..views.base import build_ipam_objects


class ListQueryCountMixin:
    """Assert a list endpoint resolves its relations without a per-row query."""

    url = None

    def _query_count(self, params):
        """Return the queries one list request issues, pinning the rows it returned."""
        expected = self.model.objects.count()
        self.assertGreater(expected, 0)
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(f"{self.url}?{params}", **self.header)
        self.assertHttpStatus(response, 200)
        # Without this an emptied response would satisfy the invariant trivially.
        self.assertEqual(response.data["count"], expected)
        return len(context.captured_queries)

    def assertQueryCountHoldsAsRowsGrow(self, params):
        """Assert adding rows leaves the query count untouched."""
        # The first request of a shape warms per-process caches, so measure warm.
        self._query_count(params)
        before = self._query_count(params)
        self.add_rows()
        self.assertEqual(self._query_count(params), before)


class ACLAssignmentListQueryTestCase(ListQueryCountMixin, APITestCase):
    """
    Brief and field-limited responses still render "display", and
    ACLAssignment.__str__() walks both access_list and assigned_object, so
    the prefetches core derives from the full serializer are not enough.
    """

    model = ACLAssignment

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("Device 1")
        cls.virtual_machine = create_test_virtualmachine("VM 1")
        cls.access_list = AccessList.objects.create(
            name="Access List 1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )
        cls.url = reverse("plugins-api:netbox_acls-api:aclassignment-list")
        cls.add_rows()

    @classmethod
    def add_rows(cls, count=2):
        """Attach the access list to `count` further interfaces of each target type."""
        offset = cls.model.objects.count()
        for index in range(offset, offset + count):
            for parent, accessor in ((cls.device, "interfaces"), (cls.virtual_machine, "interfaces")):
                interface = getattr(parent, accessor).create(
                    name=f"Interface {index}",
                    **({"type": InterfaceTypeChoices.TYPE_1GE_FIXED} if parent is cls.device else {}),
                )
                ACLAssignment.objects.create(
                    access_list=cls.access_list,
                    assigned_object=interface,
                    direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
                )

    def test_narrowed_list_query_count_is_independent_of_row_count(self):
        """Test a brief or field-limited list does not resolve display one row at a time.

        The full response is excluded: its nested target serializer walks
        Interface.device, which a plain prefetch lookup cannot reach through a
        generic foreign key. That growth predates this test.
        """
        self.add_permissions("netbox_acls.view_aclassignment")
        for params in ("brief=1", "fields=id,display"):
            with self.subTest(params=params):
                self.assertQueryCountHoldsAsRowsGrow(params)


class ACLRuleListQueryTestCase(ListQueryCountMixin, APITestCase):
    """ACLRule.__str__() walks access_list, which the narrowed shapes still render."""

    @classmethod
    def setUpTestData(cls):
        cls.aggregate, cls.prefix, cls.ip_address, cls.ip_range = build_ipam_objects()
        cls.standard_acl = AccessList.objects.create(
            name="Standard ACL",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )
        cls.extended_acl = AccessList.objects.create(
            name="Extended ACL",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )
        cls.add_rows()

    @classmethod
    def add_rows(cls, count=2):
        """Add `count` further rules to each concrete rule type."""
        offset = ACLStandardRule.objects.count()
        for index in range(offset, offset + count):
            sequence = (index + 1) * 10
            ACLStandardRule.objects.create(
                access_list=cls.standard_acl,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=cls.prefix,
            )
            ACLExtendedRule.objects.create(
                access_list=cls.extended_acl,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=cls.prefix,
                destination=cls.ip_address,
            )

    def test_narrowed_list_query_count_is_independent_of_row_count(self):
        """Test neither rule endpoint resolves its access list one row at a time."""
        self.add_permissions(
            "netbox_acls.view_aclstandardrule",
            "netbox_acls.view_aclextendedrule",
        )
        cases = (
            (ACLStandardRule, "plugins-api:netbox_acls-api:aclstandardrule-list"),
            (ACLExtendedRule, "plugins-api:netbox_acls-api:aclextendedrule-list"),
        )
        for model, url_name in cases:
            self.model = model
            self.url = reverse(url_name)
            for params in ("brief=1", "fields=id,display"):
                with self.subTest(model=model.__name__, params=params):
                    self.assertQueryCountHoldsAsRowsGrow(params)
