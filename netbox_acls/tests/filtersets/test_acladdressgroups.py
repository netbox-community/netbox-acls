from django.test import TestCase

from utilities.testing import ChangeLoggedFilterSetTestMixin

from ...choices import ACLAddressFamilyChoices
from ...filtersets import ACLAddressGroupFilterSet
from ...models import ACLAddressGroup


class ACLAddressGroupFilterSetTestCase(TestCase, ChangeLoggedFilterSetTestMixin):
    """FilterSet tests for ACLAddressGroup."""

    queryset = ACLAddressGroup.objects.all()
    filterset = ACLAddressGroupFilterSet

    @classmethod
    def setUpTestData(cls):
        ACLAddressGroup.objects.create(
            name="v4",
            description="Trusted clients",
        )
        ACLAddressGroup.objects.create(
            name="v6",
            family=ACLAddressFamilyChoices.FAMILY_IPV6,
            comments="Reviewed",
        )
        ACLAddressGroup.objects.create(
            name="other",
        )

    def test_q(self):
        params = {"q": "v4"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"q": "clients"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"q": "Reviewed"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_ignores_choice_values(self):
        """Searching for a family value matches nothing."""
        params = {"q": ACLAddressFamilyChoices.FAMILY_IPV6}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_q_ignores_blank_terms(self):
        """Ignoring a blank term means returning everything, not nothing."""
        self.assertEqual(self.filterset({"q": "   "}, self.queryset).qs.count(), 3)

    def test_name(self):
        params = {"name": ["v4", "v6"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["Trusted clients"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_comments(self):
        params = {"comments": "Reviewed"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_family(self):
        filterset = self.filterset({"family": [ACLAddressFamilyChoices.FAMILY_IPV4]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 2)
        params = {"family": [ACLAddressFamilyChoices.FAMILY_IPV4, ACLAddressFamilyChoices.FAMILY_IPV6]}
        filterset = self.filterset(params, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 3)

    def test_family_rejects_dual(self):
        filterset = self.filterset({"family": ["dual"]}, self.queryset)
        self.assertIn("family", filterset.errors)
