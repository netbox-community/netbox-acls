"""Tests that list endpoints resolve their relations in a bounded number of queries."""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from utilities.testing import APITestCase, create_test_device

from ...choices import ACLAssignmentDirectionChoices, ACLFamilyChoices, ACLTypeChoices
from ...models import AccessList, ACLAssignment


class ACLAssignmentListQueryTestCase(APITestCase):
    """
    A list response must not issue one query per row.

    Brief and field-limited responses still render "display", and
    ACLAssignment.__str__() walks both access_list and assigned_object, so
    the prefetches core derives from the full serializer are not enough.
    """

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("Device 1")
        cls.access_list = AccessList.objects.create(
            name="Access List 1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )
        cls.url = reverse("plugins-api:netbox_acls-api:aclassignment-list")
        cls.add_assignments(2)

    @classmethod
    def add_assignments(cls, count):
        """Attach the access list to `count` further new interfaces."""
        existing = Interface.objects.filter(device=cls.device).count()
        for index in range(existing, existing + count):
            interface = Interface.objects.create(
                device=cls.device,
                name=f"Interface {index}",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            )
            ACLAssignment.objects.create(
                access_list=cls.access_list,
                assigned_object=interface,
                direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
            )

    def _query_count(self, params):
        """Return the number of queries a list request issues."""
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(f"{self.url}?{params}", **self.header)
        self.assertHttpStatus(response, 200)
        return len(context.captured_queries)

    def test_narrowed_list_query_count_is_independent_of_row_count(self):
        """Test a brief or field-limited list does not resolve display one row at a time.

        The full response is excluded: its nested target serializer walks
        Interface.device, which no prefetch reaches through a generic foreign
        key. That growth predates this test and is tracked separately.
        """
        self.add_permissions("netbox_acls.view_aclassignment")
        for params in ("brief=1", "fields=id,display"):
            with self.subTest(params=params):
                # The first request of a shape warms per-process caches, so measure warm.
                self._query_count(params)
                before = self._query_count(params)
                self.add_assignments(4)
                self.assertEqual(self._query_count(params), before)
