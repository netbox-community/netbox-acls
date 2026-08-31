from django.test import TestCase

from utilities.testing import ChangeLoggedFilterSetTestMixin

from ...choices import ACLActionChoices, ACLFamilyChoices, ACLTypeChoices
from ...filtersets import AccessListFilterSet
from ...models import AccessList


class AccessListFilterSetTestCase(TestCase, ChangeLoggedFilterSetTestMixin):
    """FilterSet tests for AccessList."""

    queryset = AccessList.objects.all()
    filterset = AccessListFilterSet

    @classmethod
    def setUpTestData(cls):
        access_lists = (
            AccessList(
                name="testacl1",
                type=ACLTypeChoices.TYPE_STANDARD,
                family=ACLFamilyChoices.FAMILY_IPV4,
                default_action=ACLActionChoices.ACTION_DENY,
                description="first list",
                comments="managed by the network team",
            ),
            AccessList(
                name="testacl2",
                type=ACLTypeChoices.TYPE_EXTENDED,
                family=ACLFamilyChoices.FAMILY_IPV6,
                default_action=ACLActionChoices.ACTION_PERMIT,
                description="second list",
                comments="managed by the security team",
            ),
            AccessList(
                name="testacl3",
                type=ACLTypeChoices.TYPE_EXTENDED,
                family=ACLFamilyChoices.FAMILY_DUAL,
                default_action=ACLActionChoices.ACTION_REJECT,
                description="third list",
                comments="unmanaged",
            ),
        )
        AccessList.objects.bulk_create(access_lists)

    def test_q(self):
        params = {"q": "testacl1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_ignores_choice_values(self):
        """Zero is correct here. The default action has its own filter."""
        params = {"q": ACLActionChoices.ACTION_REJECT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_q_ignores_blank_terms(self):
        """Ignoring a blank term means returning everything, not nothing."""
        self.assertEqual(self.filterset({"q": "   "}, self.queryset).qs.count(), 3)

    def test_name(self):
        params = {"name": ["testacl1", "testacl2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["first list"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    # comments is a TextField, which django-filter maps to a single-valued CharFilter
    # matching exactly, unlike the CharField-backed description above. Pass a scalar and
    # the whole value, and use the generated comments__ic lookup for a substring match.

    def test_comments(self):
        params = {"comments": "unmanaged"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"comments__ic": "managed by"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    # type, family and default_action are single-valued ChoiceFilters, matching the
    # single-select widgets in AccessListFilterForm. Passing a list silently matches
    # everything, so these must be asserted one value at a time.

    def test_type(self):
        params = {"type": ACLTypeChoices.TYPE_EXTENDED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"type": ACLTypeChoices.TYPE_STANDARD}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_family(self):
        params = {"family": ACLFamilyChoices.FAMILY_IPV4}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"family": ACLFamilyChoices.FAMILY_DUAL}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_default_action(self):
        params = {"default_action": ACLActionChoices.ACTION_DENY}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"default_action": ACLActionChoices.ACTION_PERMIT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
