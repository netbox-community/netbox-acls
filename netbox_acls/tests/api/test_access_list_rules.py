from rest_framework import status

from ipam.models import Prefix
from netbox_acls.choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from utilities.testing import APIViewTestCases

from ...models import AccessList, ACLExtendedRule, ACLStandardRule


class ACLStandardRuleAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLStandardRule.
    """

    model = ACLStandardRule
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["access_list", "display", "id", "sequence", "url"]
    user_permissions = (
        "ipam.view_prefix",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        """Set up ACL Standard Rule for API view testing."""

        # AccessList
        cls.access_list_device = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        access_list_vm = AccessList.objects.create(
            name="testacl2",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        # Prefix
        prefix1 = Prefix.objects.create(
            prefix="10.0.0.0/24",
        )
        prefix2 = Prefix.objects.create(
            prefix="10.0.1.0/24",
        )

        acl_standard_rules = (
            ACLStandardRule(
                access_list=cls.access_list_device,
                sequence=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=prefix1,
            ),
            ACLStandardRule(
                access_list=cls.access_list_device,
                sequence=20,
                description="Rule 20",
                action=ACLRuleActionChoices.ACTION_REMARK,
                remark="Remark 1",
            ),
            ACLStandardRule(
                access_list=access_list_vm,
                sequence=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_DENY,
                remark="Deny prefix",
                source=prefix2,
            ),
        )
        ACLStandardRule.objects.bulk_create(acl_standard_rules)

        cls.create_data = [
            {
                "access_list": cls.access_list_device.id,
                "sequence": 30,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_DENY,
                "source_type": "ipam.prefix",
                "source_id": prefix2.id,
            },
            {
                "access_list": access_list_vm.id,
                "sequence": 20,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "remark": "Permit prefix",
                "source_type": "ipam.prefix",
                "source_id": prefix1.id,
            },
            {
                "access_list": access_list_vm.id,
                "sequence": 30,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_REMARK,
                "remark": "Remark 2",
            },
        ]
        cls.bulk_update_data = {
            "description": "Rule bulk update",
        }

    def test_remark_action_requires_a_remark(self):
        """
        The model's clean() is the only source of this message, reached via full_clean().

        Sequence 100 stays clear of the rules setUpTestData already created on this
        access list.
        """
        self.add_permissions("netbox_acls.add_aclstandardrule")
        response = self.client.post(
            self._get_list_url(),
            {
                "access_list": self.access_list_device.pk,
                "sequence": 100,
                "action": ACLRuleActionChoices.ACTION_REMARK,
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["remark"],
            ["When the action is 'remark', a remark is required."],
        )

    def test_remark_action_accepts_a_rule_that_already_has_a_remark(self):
        """Test that a partial update need not resend the remark alongside the action."""
        rule = ACLStandardRule.objects.get(access_list=self.access_list_device, sequence=20)
        self.assertTrue(rule.remark)

        self.add_permissions("netbox_acls.change_aclstandardrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {"action": ACLRuleActionChoices.ACTION_REMARK},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_source_fields_are_optional(self):
        """A rule with neither a source type nor a source is valid, only a half-set pair is not."""
        self.add_permissions("netbox_acls.add_aclstandardrule")
        response = self.client.post(
            self._get_list_url(),
            {
                "access_list": self.access_list_device.pk,
                "sequence": 110,
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_type": None,
                "source_id": None,
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_201_CREATED)


class ACLExtendedRuleAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLExtendedRule.
    """

    model = ACLExtendedRule
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["access_list", "display", "id", "sequence", "url"]
    user_permissions = (
        "ipam.view_prefix",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        """Set up ACL Extended Rule for API view testing."""

        # AccessList
        cls.access_list_device = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        access_list_vm = AccessList.objects.create(
            name="testacl2",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        # Prefix
        prefix1 = Prefix.objects.create(
            prefix="10.0.0.0/24",
        )
        prefix2 = Prefix.objects.create(
            prefix="10.0.1.0/24",
        )

        acl_extended_rules = (
            ACLExtendedRule(
                access_list=cls.access_list_device,
                sequence=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_PERMIT,
                remark="Permit prefix",
                protocol=ACLProtocolChoices.PROTOCOL_TCP,
                source=prefix1,
                source_port_ranges=[[1024, 65535]],
                destination=prefix1,
                destination_port_ranges=[[22, 23], [443, 444]],
            ),
            ACLExtendedRule(
                access_list=cls.access_list_device,
                sequence=20,
                description="Rule 20",
                action=ACLRuleActionChoices.ACTION_REMARK,
                remark="Remark 1",
            ),
            ACLExtendedRule(
                access_list=access_list_vm,
                sequence=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_DENY,
                source=prefix2,
                destination=prefix1,
            ),
        )
        ACLExtendedRule.objects.bulk_create(acl_extended_rules)

        cls.create_data = [
            {
                "access_list": cls.access_list_device.id,
                "sequence": 30,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_DENY,
                "protocol": ACLProtocolChoices.PROTOCOL_UDP,
                "remark": "Deny prefix",
                "source_type": "ipam.prefix",
                "source_id": prefix2.id,
                "source_port_ranges": [[53, 53], [123, 123]],
                "destination_type": "ipam.prefix",
                "destination_id": prefix2.id,
                "destination_port_ranges": [[53, 53]],
            },
            {
                "access_list": access_list_vm.id,
                "sequence": 20,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "protocol": ACLProtocolChoices.PROTOCOL_ICMP,
                "source_type": "ipam.prefix",
                "source_id": prefix1.id,
                "destination_type": "ipam.prefix",
                "destination_id": prefix2.id,
            },
            {
                "access_list": access_list_vm.id,
                "sequence": 30,
                "description": "Rule 30",
                "action": ACLRuleActionChoices.ACTION_REMARK,
                "remark": "Remark 2",
            },
        ]
        cls.bulk_update_data = {
            "description": "Rule bulk update",
        }

    def test_remark_action_requires_a_remark(self):
        """The model's clean() is the only source of this message, reached via full_clean()."""
        self.add_permissions("netbox_acls.add_aclextendedrule")
        response = self.client.post(
            self._get_list_url(),
            {
                "access_list": self.access_list_device.pk,
                "sequence": 100,
                "action": ACLRuleActionChoices.ACTION_REMARK,
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["remark"],
            ["When the action is 'remark', a remark is required."],
        )

    def test_remark_action_accepts_a_rule_that_already_has_a_remark(self):
        """Test that a partial update need not resend the remark alongside the action."""
        rule = ACLExtendedRule.objects.get(access_list=self.access_list_device, sequence=20)
        self.assertTrue(rule.remark)

        self.add_permissions("netbox_acls.change_aclextendedrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {"action": ACLRuleActionChoices.ACTION_REMARK},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_remark_action_rejects_a_protocol(self):
        """One of the four extra conditions only an extended rule can fail."""
        self.add_permissions("netbox_acls.add_aclextendedrule")
        response = self.client.post(
            self._get_list_url(),
            {
                "access_list": self.access_list_device.pk,
                "sequence": 110,
                "action": ACLRuleActionChoices.ACTION_REMARK,
                "remark": "Remark",
                "protocol": ACLProtocolChoices.PROTOCOL_TCP,
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["protocol"],
            ["When the action is 'remark', Protocol must not be set."],
        )

    def test_remark_action_rejects_source_ports(self):
        """Port ranges post as pairs, the shape create_data already uses."""
        self.add_permissions("netbox_acls.add_aclextendedrule")
        response = self.client.post(
            self._get_list_url(),
            {
                "access_list": self.access_list_device.pk,
                "sequence": 120,
                "action": ACLRuleActionChoices.ACTION_REMARK,
                "remark": "Remark",
                "source_port_ranges": [[80, 80]],
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["source_port_ranges"],
            ["When the action is 'remark', Source Ports must not be set."],
        )
