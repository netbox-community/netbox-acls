"""Tests for the ACL fields contributed to NetBox's own GraphQL types."""

import re

from django.test import SimpleTestCase
from django.urls import reverse

from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from ipam.models import Prefix
from utilities.testing import APITestCase, create_test_device

from ...choices import (
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule

ASSIGNMENT_FIELDS = ("acl_assignments: [ACLAssignmentType!]!",)

RULE_FIELDS = (
    "acl_standard_rule_sources: [ACLStandardRuleType!]!",
    "acl_extended_rule_sources: [ACLExtendedRuleType!]!",
    "acl_extended_rule_destinations: [ACLExtendedRuleType!]!",
)

CORE_TYPE_FIELDS = {
    "DeviceType": ASSIGNMENT_FIELDS,
    "InterfaceType": ASSIGNMENT_FIELDS,
    "VirtualChassisType": ASSIGNMENT_FIELDS,
    "VirtualMachineType": ASSIGNMENT_FIELDS,
    "VMInterfaceType": ASSIGNMENT_FIELDS,
    "AggregateType": RULE_FIELDS,
    "IPAddressType": RULE_FIELDS,
    "IPRangeType": RULE_FIELDS,
    "PrefixType": RULE_FIELDS,
}


class GraphQLSchemaExtensionTestCase(SimpleTestCase):
    """Test case for the ACL fields spliced into NetBox's core object types."""

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from netbox.graphql.schema import schema

        cls.schema_str = schema.as_str()

    def test_core_types_carry_the_acl_fields(self):
        """Test every contributed generic relation has a matching GraphQL field."""
        for type_name, field_names in CORE_TYPE_FIELDS.items():
            block = re.search(rf"\ntype {type_name} \{{.*?\n\}}", self.schema_str, re.DOTALL)
            self.assertIsNotNone(block, f"{type_name} not found in the GraphQL schema")
            for signature in field_names:
                with self.subTest(type=type_name, field=signature):
                    self.assertIn(signature, block.group(0))


class GraphQLTypeExtensionQueryTestCase(APITestCase):
    """Test case for resolving the ACL fields on NetBox's core object types."""

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("Device 1")
        cls.interface = Interface.objects.create(
            device=cls.device,
            name="Interface 1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.prefix = Prefix.objects.create(prefix="10.0.0.0/24")

        standard_acl = AccessList.objects.create(
            name="Standard ACL",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )
        extended_acl = AccessList.objects.create(
            name="Extended ACL",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
        )
        cls.assignment = ACLAssignment.objects.create(
            access_list=standard_acl,
            assigned_object=cls.interface,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )
        cls.standard_rule = ACLStandardRule.objects.create(
            access_list=standard_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=cls.prefix,
        )
        cls.extended_rule = ACLExtendedRule.objects.create(
            access_list=extended_acl,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=cls.prefix,
            destination=cls.prefix,
        )

    def _query(self, query):
        """Post a GraphQL query as the test user and return the parsed data."""
        response = self.client.post(
            reverse("graphql"),
            data={"query": query},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, 200)
        body = response.json()
        self.assertNotIn("errors", body, body)
        return body["data"]

    def test_interface_exposes_its_acl_assignments(self):
        """Test the Interface type reaches the ACL assignments attached to it."""
        self.add_permissions("dcim.view_interface", "netbox_acls.view_aclassignment")
        data = self._query(f"{{ interface(id: {self.interface.pk}) {{ acl_assignments {{ id direction }} }} }}")
        self.assertEqual(
            data["interface"]["acl_assignments"],
            [
                {
                    "id": str(self.assignment.pk),
                    "direction": ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
                }
            ],
        )

    def test_assignments_are_hidden_without_the_view_permission(self):
        """Test a user who may not view ACL assignments sees none through the core type.

        Core enforces this in BaseObjectType.get_queryset(), so the field cannot
        leak even though RestrictedPrefetch only narrows what gets cached.
        """
        self.add_permissions("dcim.view_interface")
        data = self._query(f"{{ interface(id: {self.interface.pk}) {{ acl_assignments {{ id }} }} }}")
        self.assertEqual(data["interface"]["acl_assignments"], [])

    def test_prefix_exposes_the_rules_referencing_it(self):
        """Test an IPAM object reaches the rules using it as source and as destination."""
        self.add_permissions(
            "ipam.view_prefix",
            "netbox_acls.view_aclstandardrule",
            "netbox_acls.view_aclextendedrule",
        )
        data = self._query(
            f"{{ prefix(id: {self.prefix.pk}) {{ "
            f"acl_standard_rule_sources {{ id }} "
            f"acl_extended_rule_sources {{ id }} "
            f"acl_extended_rule_destinations {{ id }} }} }}"
        )
        self.assertEqual(data["prefix"]["acl_standard_rule_sources"], [{"id": str(self.standard_rule.pk)}])
        self.assertEqual(data["prefix"]["acl_extended_rule_sources"], [{"id": str(self.extended_rule.pk)}])
        self.assertEqual(data["prefix"]["acl_extended_rule_destinations"], [{"id": str(self.extended_rule.pk)}])
