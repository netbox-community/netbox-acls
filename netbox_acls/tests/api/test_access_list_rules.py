from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from ipam.models import Prefix
from netbox_acls.choices import (
    ACLActionChoices,
    ACLAddressFamilyChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTCPFlagChoices,
    ACLTCPFlagMatchChoices,
    ACLTypeChoices,
)
from utilities.testing import APIViewTestCases

from ...models import AccessList, ACLAddressGroup, ACLExtendedRule, ACLStandardRule


class GraphQLQueryMixin:
    """Run GraphQL queries through the API test client."""

    def _post_graphql_query(self, query):
        """Return the data payload of a successful GraphQL query."""
        response = self.client.post(
            reverse("graphql"),
            data={"query": query},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)
        payload = response.json()
        self.assertNotIn("errors", payload)
        return payload["data"]


class ACLStandardRuleAPIViewTestCase(GraphQLQueryMixin, APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLStandardRule.
    """

    model = ACLStandardRule
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["access_list", "display", "id", "sequence", "url"]
    user_permissions = (
        "ipam.view_prefix",
        "netbox_acls.view_accesslist",
        "netbox_acls.view_acladdressgroup",
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

        # Address Group
        address_group = ACLAddressGroup.objects.create(
            name="address-group-1",
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
            {
                "access_list": access_list_vm.id,
                "sequence": 40,
                "description": "Rule 40",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_type": "netbox_acls.acladdressgroup",
                "source_id": address_group.id,
            },
        ]
        cls.bulk_update_data = {
            "description": "Rule bulk update",
        }
        cls.bulk_update_invalid_data = {
            "action": "sideways",
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

    def test_create_with_logging(self):
        """Test that a rule can be created with logging enabled."""
        self.add_permissions("netbox_acls.add_aclstandardrule")
        data = {**self.create_data[0], "sequence": 500, "log_matches": True, "log_options": ["syslog"]}
        response = self.client.post(self._get_list_url(), data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertTrue(response.data["log_matches"])
        self.assertEqual(response.data["log_options"], ["syslog"])

    def test_create_rejects_options_without_log_matches(self):
        """Test that the API rejects options while logging is disabled."""
        self.add_permissions("netbox_acls.add_aclstandardrule")
        data = {**self.create_data[0], "sequence": 510, "log_matches": False, "log_options": ["syslog"]}
        response = self.client.post(self._get_list_url(), data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_patch_disabling_logging_requires_clearing_options(self):
        """Test that disabling logging does not silently discard the options."""
        rule = ACLStandardRule.objects.create(
            access_list=self.access_list_device,
            sequence=520,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            log_matches=True,
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        self.add_permissions("netbox_acls.change_aclstandardrule")
        url = self._get_detail_url(rule)
        self.assertHttpStatus(
            self.client.patch(url, {"log_matches": False}, format="json", **self.header),
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertHttpStatus(
            self.client.patch(url, {"log_matches": False, "log_options": []}, format="json", **self.header),
            status.HTTP_200_OK,
        )

    def test_create_normalizes_duplicate_and_unordered_options(self):
        """Test that REST create stores options canonically, as model clean does."""
        self.add_permissions("netbox_acls.add_aclstandardrule")
        data = {
            **self.create_data[0],
            "sequence": 530,
            "log_matches": True,
            "log_options": [
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
                ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
            ],
        }
        response = self.client.post(self._get_list_url(), data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["log_options"], ["cisco-log-input", "syslog"])

        rule = ACLStandardRule.objects.get(pk=response.data["id"])
        self.assertEqual(rule.log_options, ["cisco-log-input", "syslog"])

    def test_patch_normalizes_duplicate_and_unordered_options(self):
        """Test that REST update stores options canonically rather than as posted."""
        rule = ACLStandardRule.objects.create(
            access_list=self.access_list_device,
            sequence=540,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            log_matches=True,
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        self.add_permissions("netbox_acls.change_aclstandardrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {
                "log_options": [
                    ACLRuleLogOptionChoices.OPTION_SYSLOG,
                    ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
                    ACLRuleLogOptionChoices.OPTION_SYSLOG,
                ]
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)

        rule.refresh_from_db()
        self.assertEqual(rule.log_options, ["cisco-log-input", "syslog"])

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_filters_narrow_by_logging_state(self):
        """Test that each logging filter narrows the result set on its own."""
        self.add_permissions("netbox_acls.view_aclstandardrule")

        # Negative control, logging disabled.
        ACLStandardRule.objects.create(
            access_list=self.access_list_device,
            sequence=600,
            action=ACLRuleActionChoices.ACTION_PERMIT,
        )
        default_logging_rule = ACLStandardRule.objects.create(
            access_list=self.access_list_device,
            sequence=610,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            log_matches=True,
        )
        syslog_rule = ACLStandardRule.objects.create(
            access_list=self.access_list_device,
            sequence=620,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            log_matches=True,
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        cisco_rule = ACLStandardRule.objects.create(
            access_list=self.access_list_device,
            sequence=630,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            log_matches=True,
            log_options=[ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT],
        )

        with self.subTest(filter="log_matches"):
            data = self._post_graphql_query(
                """
                {
                    acl_standard_rule_list(filters: {log_matches: {exact: true}}) {
                        id
                    }
                }
                """
            )
            self.assertEqual(
                sorted(rule["id"] for rule in data["acl_standard_rule_list"]),
                sorted(str(rule.pk) for rule in (default_logging_rule, syslog_rule, cisco_rule)),
            )

        with self.subTest(filter="log_options"):
            data = self._post_graphql_query(
                """
                {
                    acl_standard_rule_list(filters: {log_options: {overlap: ["syslog"]}}) {
                        id
                        log_matches
                        log_options
                    }
                }
                """
            )
            self.assertEqual(
                data["acl_standard_rule_list"],
                [
                    {
                        "id": str(syslog_rule.pk),
                        "log_matches": True,
                        "log_options": [ACLRuleLogOptionChoices.OPTION_SYSLOG],
                    },
                ],
            )

    def test_filter_accepts_repeated_action_parameters(self):
        """Repeated parameters must reach the filter set and be ORed, not overwrite each other."""
        self.add_permissions("netbox_acls.view_aclstandardrule")
        url = (
            f"{self._get_list_url()}"
            f"?action={ACLRuleActionChoices.ACTION_PERMIT}"
            f"&action={ACLRuleActionChoices.ACTION_DENY}"
        )
        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_create_rejects_an_address_group_of_another_family(self):
        """Test that an IPv4 access list rejects an IPv6 address group as source."""
        self.add_permissions("netbox_acls.add_aclstandardrule")
        address_group = ACLAddressGroup.objects.create(
            name="address-group-v6",
            family=ACLAddressFamilyChoices.FAMILY_IPV6,
        )
        data = {
            **self.create_data[0],
            "sequence": 550,
            "source_type": "netbox_acls.acladdressgroup",
            "source_id": address_group.id,
        }
        response = self.client.post(self._get_list_url(), data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)


class ACLExtendedRuleAPIViewTestCase(GraphQLQueryMixin, APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLExtendedRule.
    """

    model = ACLExtendedRule
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["access_list", "display", "id", "sequence", "url"]
    user_permissions = (
        "ipam.view_prefix",
        "netbox_acls.view_accesslist",
        "netbox_acls.view_acladdressgroup",
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
        access_list_dual = AccessList.objects.create(
            name="testacl3",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_DUAL,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # Prefix
        prefix1 = Prefix.objects.create(
            prefix="10.0.0.0/24",
        )
        prefix2 = Prefix.objects.create(
            prefix="10.0.1.0/24",
        )

        # Address Group
        address_group = ACLAddressGroup.objects.create(
            name="address-group-1",
        )

        acl_extended_rules = (
            ACLExtendedRule(
                access_list=cls.access_list_device,
                sequence=10,
                description="Rule 10",
                action=ACLRuleActionChoices.ACTION_PERMIT,
                remark="Permit prefix",
                protocol=ACLProtocolChoices.PROTOCOL_TCP,
                tcp_flags=[ACLTCPFlagChoices.FLAG_ACK, ACLTCPFlagChoices.FLAG_RST],
                tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY,
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
                protocol=ACLProtocolChoices.PROTOCOL_ICMP,
                icmp_type=0,
                icmp_code=0,
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
                "tcp_flags": [],
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
                "icmp_type": 0,
                "icmp_code": 0,
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
            {
                "access_list": access_list_vm.id,
                "sequence": 40,
                "description": "Rule 40",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "protocol": ACLProtocolChoices.PROTOCOL_GRE,
                "source_type": "ipam.prefix",
                "source_id": prefix1.id,
                "destination_type": "ipam.prefix",
                "destination_id": prefix2.id,
            },
            {
                "access_list": access_list_vm.id,
                "sequence": 50,
                "description": "Rule 50",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "protocol": ACLProtocolChoices.PROTOCOL_TCP,
                "tcp_flags": [ACLTCPFlagChoices.FLAG_RST, ACLTCPFlagChoices.FLAG_ACK],
                "tcp_flags_match": ACLTCPFlagMatchChoices.MATCH_ANY,
                "source_type": "netbox_acls.acladdressgroup",
                "source_id": address_group.id,
                "destination_type": "netbox_acls.acladdressgroup",
                "destination_id": address_group.id,
            },
            {
                "access_list": access_list_dual.id,
                "sequence": 10,
                "description": "Rule 10",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "protocol": ACLProtocolChoices.PROTOCOL_ICMPV6,
                "icmp_type": 128,
                "icmp_code": 0,
            },
        ]
        cls.bulk_update_data = {
            "description": "Rule bulk update",
        }
        cls.bulk_update_invalid_data = {
            "action": "sideways",
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

    def test_create_with_logging(self):
        """Test that a rule can be created with logging enabled."""
        self.add_permissions("netbox_acls.add_aclextendedrule")
        data = {**self.create_data[0], "sequence": 500, "log_matches": True, "log_options": ["syslog"]}
        response = self.client.post(self._get_list_url(), data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertTrue(response.data["log_matches"])
        self.assertEqual(response.data["log_options"], ["syslog"])

    def test_create_rejects_options_without_log_matches(self):
        """Test that the API rejects options while logging is disabled."""
        self.add_permissions("netbox_acls.add_aclextendedrule")
        data = {**self.create_data[0], "sequence": 510, "log_matches": False, "log_options": ["syslog"]}
        response = self.client.post(self._get_list_url(), data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_patch_disabling_logging_requires_clearing_options(self):
        """Test that disabling logging does not silently discard the options."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=520,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            log_matches=True,
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        self.add_permissions("netbox_acls.change_aclextendedrule")
        url = self._get_detail_url(rule)
        self.assertHttpStatus(
            self.client.patch(url, {"log_matches": False}, format="json", **self.header),
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertHttpStatus(
            self.client.patch(url, {"log_matches": False, "log_options": []}, format="json", **self.header),
            status.HTTP_200_OK,
        )

    def test_create_normalizes_duplicate_and_unordered_options(self):
        """Test that REST create stores options canonically, as model clean does."""
        self.add_permissions("netbox_acls.add_aclextendedrule")
        data = {
            **self.create_data[0],
            "sequence": 530,
            "log_matches": True,
            "log_options": [
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
                ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
            ],
        }
        response = self.client.post(self._get_list_url(), data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["log_options"], ["cisco-log-input", "syslog"])

        rule = ACLExtendedRule.objects.get(pk=response.data["id"])
        self.assertEqual(rule.log_options, ["cisco-log-input", "syslog"])

    def test_patch_normalizes_duplicate_and_unordered_options(self):
        """Test that REST update stores options canonically rather than as posted."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=540,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            log_matches=True,
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        self.add_permissions("netbox_acls.change_aclextendedrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {
                "log_options": [
                    ACLRuleLogOptionChoices.OPTION_SYSLOG,
                    ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
                    ACLRuleLogOptionChoices.OPTION_SYSLOG,
                ]
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)

        rule.refresh_from_db()
        self.assertEqual(rule.log_options, ["cisco-log-input", "syslog"])

    def test_create_normalizes_duplicate_and_unordered_tcp_flags(self):
        """Test that REST create stores TCP flags canonically, as model clean does."""
        self.add_permissions("netbox_acls.add_aclextendedrule")
        data = {
            **self.create_data[4],
            "sequence": 550,
            "tcp_flags": [
                ACLTCPFlagChoices.FLAG_ACK,
                ACLTCPFlagChoices.FLAG_SYN,
                ACLTCPFlagChoices.FLAG_ACK,
            ],
        }
        response = self.client.post(self._get_list_url(), data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tcp_flags"], ["syn", "ack"])

        rule = ACLExtendedRule.objects.get(pk=response.data["id"])
        self.assertEqual(rule.tcp_flags, ["syn", "ack"])

    def test_patch_normalizes_duplicate_and_unordered_tcp_flags(self):
        """Test that REST update stores TCP flags canonically rather than as posted."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=560,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            tcp_flags=[ACLTCPFlagChoices.FLAG_ACK],
        )
        self.add_permissions("netbox_acls.change_aclextendedrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {
                "tcp_flags": [
                    ACLTCPFlagChoices.FLAG_ACK,
                    ACLTCPFlagChoices.FLAG_SYN,
                    ACLTCPFlagChoices.FLAG_ACK,
                ]
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)

        rule.refresh_from_db()
        self.assertEqual(rule.tcp_flags, ["syn", "ack"])

    def test_patch_changing_protocol_with_retained_tcp_flags_is_rejected(self):
        """Test that a protocol change is rejected while incompatible TCP flags remain set."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=570,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            tcp_flags=[ACLTCPFlagChoices.FLAG_ACK, ACLTCPFlagChoices.FLAG_RST],
            tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY,
        )
        self.add_permissions("netbox_acls.change_aclextendedrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {"protocol": ACLProtocolChoices.PROTOCOL_UDP},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tcp_flags", response.data)

    def test_patch_changing_protocol_and_clearing_tcp_flags_succeeds(self):
        """Test that changing the protocol succeeds once the TCP flags are cleared."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=580,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            tcp_flags=[ACLTCPFlagChoices.FLAG_ACK, ACLTCPFlagChoices.FLAG_RST],
            tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY,
        )
        self.add_permissions("netbox_acls.change_aclextendedrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {"protocol": ACLProtocolChoices.PROTOCOL_UDP, "tcp_flags": []},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)

        rule.refresh_from_db()
        self.assertEqual(rule.tcp_flags, [])

    def test_patch_clearing_an_icmp_type_with_a_retained_code_is_rejected(self):
        """Test that clearing an ICMP type is rejected while its code remains set."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=590,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            icmp_type=8,
            icmp_code=0,
        )
        self.add_permissions("netbox_acls.change_aclextendedrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {"icmp_type": None},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("icmp_code", response.data)

    def test_patch_changing_protocol_to_icmpv6_in_an_ipv4_acl_is_rejected(self):
        """Test that an IPv4 ACL rejects a rule switched to ICMPv6."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=600,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
        )
        self.add_permissions("netbox_acls.change_aclextendedrule")
        response = self.client.patch(
            self._get_detail_url(rule),
            {"protocol": ACLProtocolChoices.PROTOCOL_ICMPV6},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("__all__", response.data)

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_tcp_flags_filter_narrows_by_overlap(self):
        """Test that the TCP flags filter returns the rules sharing a flag."""
        self.add_permissions("netbox_acls.view_aclextendedrule")
        fin_rule = ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=610,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            tcp_flags=[ACLTCPFlagChoices.FLAG_FIN, ACLTCPFlagChoices.FLAG_SYN],
        )
        ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=620,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            tcp_flags=[ACLTCPFlagChoices.FLAG_SYN],
        )

        data = self._post_graphql_query(
            """
            {
                acl_extended_rule_list(filters: {tcp_flags: {overlap: ["fin", "urg"]}}) {
                    id
                }
            }
            """
        )
        self.assertEqual(
            [rule["id"] for rule in data["acl_extended_rule_list"]],
            [str(fin_rule.pk)],
        )

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_tcp_flags_match_filter_narrows_by_mode(self):
        """Test that the TCP flags match filter returns the rules of one mode."""
        self.add_permissions("netbox_acls.view_aclextendedrule")
        any_rule = ACLExtendedRule.objects.get(access_list=self.access_list_device, sequence=10)
        self.assertEqual(any_rule.tcp_flags_match, ACLTCPFlagMatchChoices.MATCH_ANY)
        ACLExtendedRule.objects.create(
            access_list=self.access_list_device,
            sequence=630,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            tcp_flags=[ACLTCPFlagChoices.FLAG_ACK],
        )

        data = self._post_graphql_query(
            """
            {
                acl_extended_rule_list(filters: {tcp_flags_match: {exact: ANY}}) {
                    id
                }
            }
            """
        )
        self.assertEqual(
            [rule["id"] for rule in data["acl_extended_rule_list"]],
            [str(any_rule.pk)],
        )

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_icmp_type_filter_matches_zero(self):
        """Test that the ICMP type filter treats zero as a value."""
        self.add_permissions("netbox_acls.view_aclextendedrule")
        zero_rule = ACLExtendedRule.objects.get(access_list__name="testacl2", sequence=10)
        self.assertEqual(zero_rule.icmp_type, 0)
        for sequence, icmp_type in ((640, 8), (650, None)):
            ACLExtendedRule.objects.create(
                access_list=self.access_list_device,
                sequence=sequence,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                protocol=ACLProtocolChoices.PROTOCOL_ICMP,
                icmp_type=icmp_type,
            )

        data = self._post_graphql_query(
            """
            {
                acl_extended_rule_list(filters: {icmp_type: {filter_lookup: {exact: 0}}}) {
                    id
                }
            }
            """
        )
        self.assertEqual(
            [rule["id"] for rule in data["acl_extended_rule_list"]],
            [str(zero_rule.pk)],
        )
