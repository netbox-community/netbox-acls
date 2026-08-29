from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.backends.postgresql.psycopg_any import NumericRange

from utilities.data import string_to_ranges

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLExtendedRule
from .base import BaseTestCase


class TestACLExtendedRule(BaseTestCase):
    """
    Test ACLExtendedRule model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Extend BaseTestCase's setUpTestData() to create additional data for testing.
        """
        super().setUpTestData()

        cls.acl_type = ACLTypeChoices.TYPE_EXTENDED
        cls.family = ACLFamilyChoices.FAMILY_IPV4
        cls.default_action = "deny"
        cls.protocol = ACLProtocolChoices.PROTOCOL_TCP

        # AccessLists
        cls.extended_acl1 = AccessList.objects.create(
            name="EXTENDED_ACL",
            type=cls.acl_type,
            family=cls.family,
            default_action=cls.default_action,
            comments="EXTENDED_ACL",
        )
        cls.extended_acl2 = AccessList.objects.create(
            name="EXTENDED_ACL",
            type=cls.acl_type,
            family=cls.family,
            default_action=cls.default_action,
            comments="EXTENDED_ACL",
        )
        cls.extended_acl_v6 = AccessList.objects.create(
            name="EXTENDED_ACL_V6",
            type=cls.acl_type,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=cls.default_action,
            comments="EXTENDED_ACL_V6",
        )
        cls.extended_acl_dual = AccessList.objects.create(
            name="EXTENDED_ACL_DUAL",
            type=cls.acl_type,
            family=ACLFamilyChoices.FAMILY_DUAL,
            default_action=cls.default_action,
            comments="EXTENDED_ACL_DUAL",
        )

    def test_acl_extended_rule_creation_success(self):
        """
        Test that ACLExtendedRule creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description=(
                "Created rule with any source, any source port, "
                "any destination, any destination port, and any protocol."
            ),
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 10)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, None)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(
            created_rule.description,
            "Created rule with any source, any source port, any destination, any destination port, and any protocol.",
        )
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_source_aggregate_creation_success(self):
        """
        Test that ACLExtendedRule with source aggregate creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=20,
            action="permit",
            remark="",
            source=self.aggregate1,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with source aggregate",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 20)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.aggregate1)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, None)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with source aggregate")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_source_ip_address_creation_success(self):
        """
        Test that ACLExtendedRule with source ip address creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=30,
            action="permit",
            remark="",
            source=self.ip_address1,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with source ip address",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 30)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.ip_address1)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, None)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with source ip address")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_source_ip_range_creation_success(self):
        """
        Test that ACLExtendedRule with source ip range creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=40,
            action="permit",
            remark="",
            source=self.ip_range1,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with source ip range",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 40)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.ip_range1)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, None)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with source ip range")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_source_prefix_creation_success(self):
        """
        Test that ACLExtendedRule with source prefix creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=50,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with source prefix",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 50)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.prefix1)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, None)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with source prefix")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_source_port_ranges_creation_success(self):
        """
        Test that ACLExtendedRule with source ports creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=70,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=string_to_ranges("22, 443"),
            destination=None,
            destination_port_ranges=None,
            protocol=self.protocol,
            description="Created rule with source ports",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 70)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.prefix1)
        self.assertEqual(created_rule.source_port_ranges, [NumericRange(22, 23), NumericRange(443, 444)])
        self.assertEqual(created_rule.destination, None)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, self.protocol)
        self.assertEqual(created_rule.description, "Created rule with source ports")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_destination_aggregate_creation_success(self):
        """
        Test that ACLExtendedRule with destination aggregate creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=80,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=self.aggregate1,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with destination aggregate",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 80)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, self.aggregate1)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with destination aggregate")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_destination_ip_address_creation_success(self):
        """
        Test that ACLExtendedRule with destination ip address creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=90,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=self.ip_address1,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with destination ip address",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 90)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, self.ip_address1)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with destination ip address")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_destination_ip_range_creation_success(self):
        """
        Test that ACLExtendedRule with destination ip range creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=100,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=self.ip_range1,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with destination ip range",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 100)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, self.ip_range1)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with destination ip range")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_destination_prefix_creation_success(self):
        """
        Test that ACLExtendedRule with destination prefix creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=110,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=self.prefix1,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with destination prefix",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 110)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, self.prefix1)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with destination prefix")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_destination_port_ranges_creation_success(self):
        """
        Test that ACLExtendedRule with destination ports creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=130,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=self.prefix1,
            destination_port_ranges=string_to_ranges("22, 443"),
            protocol=self.protocol,
            description="Created rule with destination ports",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 130)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, self.prefix1)
        self.assertEqual(created_rule.destination_port_ranges, [NumericRange(22, 23), NumericRange(443, 444)])
        self.assertEqual(created_rule.protocol, self.protocol)
        self.assertEqual(created_rule.description, "Created rule with destination ports")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_ip_protocol_creation_success(self):
        """
        Test that ACLExtendedRule with IP protocol creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=140,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=None,
            destination=self.prefix2,
            destination_port_ranges=None,
            protocol=ACLProtocolChoices.PROTOCOL_IP,
            description="Created rule with IP protocol",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 140)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.prefix1)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, self.prefix2)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, ACLProtocolChoices.PROTOCOL_IP)
        self.assertEqual(created_rule.description, "Created rule with IP protocol")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_icmp_protocol_creation_success(self):
        """
        Test that ACLExtendedRule with ICMP protocol creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=140,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=None,
            destination=self.prefix2,
            destination_port_ranges=None,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            description="Created rule with ICMP protocol",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 140)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.prefix1)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, self.prefix2)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, ACLProtocolChoices.PROTOCOL_ICMP)
        self.assertEqual(created_rule.description, "Created rule with ICMP protocol")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_routing_protocol_creation_success(self):
        """
        Test that ACLExtendedRule with a routing or tunneling protocol passes validation.
        """
        routing_protocols = (
            ACLProtocolChoices.PROTOCOL_GRE,
            ACLProtocolChoices.PROTOCOL_EIGRP,
            ACLProtocolChoices.PROTOCOL_OSPF,
            ACLProtocolChoices.PROTOCOL_PIM,
        )

        for protocol in routing_protocols:
            with self.subTest(protocol=protocol):
                created_rule = ACLExtendedRule(
                    access_list=self.extended_acl1,
                    sequence=140,
                    action="permit",
                    remark="",
                    source=self.prefix1,
                    source_port_ranges=None,
                    destination=self.prefix2,
                    destination_port_ranges=None,
                    protocol=protocol,
                    description=f"Created rule with {protocol} protocol",
                )
                created_rule.full_clean()

                self.assertEqual(created_rule.protocol, protocol)
                self.assertEqual(created_rule.source, self.prefix1)
                self.assertEqual(created_rule.destination, self.prefix2)
                self.assertEqual(created_rule.source_port_ranges, [])
                self.assertEqual(created_rule.destination_port_ranges, [])

    def test_acl_extended_rule_complete_params_creation_success(self):
        """
        Test that ACLExtendedRule with complete parameters creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=150,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=string_to_ranges("1024-65535"),
            destination=self.prefix2,
            destination_port_ranges=string_to_ranges("22,443"),
            protocol=self.protocol,
            description="Created rule with complete parameters",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 150)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source, self.prefix1)
        self.assertEqual(created_rule.source_port_ranges, [NumericRange(1024, 65536)])
        self.assertEqual(created_rule.destination, self.prefix2)
        self.assertEqual(created_rule.destination_port_ranges, [NumericRange(22, 23), NumericRange(443, 444)])
        self.assertEqual(created_rule.protocol, self.protocol)
        self.assertEqual(created_rule.description, "Created rule with complete parameters")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_remark_creation_success(self):
        """
        Test that ACLExtendedRule with remark creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=160,
            action="remark",
            remark="Test remark",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with remark",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 160)
        self.assertEqual(created_rule.action, "remark")
        self.assertEqual(created_rule.remark, "Test remark")
        self.assertEqual(created_rule.source, None)
        self.assertEqual(created_rule.source_port_ranges, [])
        self.assertEqual(created_rule.destination, None)
        self.assertEqual(created_rule.destination_port_ranges, [])
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with remark")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_action_permit_with_remark_success(self):
        """
        Test that ACLExtendedRule with action 'permit' and remark passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=120,
            action="permit",
            remark="Inline remark",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created permit rule with remark",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.sequence, 120)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "Inline remark")
        self.assertEqual(created_rule.description, "Created permit rule with remark")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_action_permit_with_shared_sequence_action_remark_fail(self):
        """
        Test that ACLExtendedRule rejects a standalone remark sharing the same sequence as a permit rule.
        """
        created_permit_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=130,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=self.protocol,
            description="Created permit rule with same sequence as remark",
        )
        created_permit_rule.full_clean()
        created_permit_rule.save()

        created_remark_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=130,
            action="remark",
            remark="Standalone remark",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created remark rule with same sequence as permit rule",
        )
        with self.assertRaises(ValidationError):
            created_remark_rule.full_clean()

    def test_access_list_standard_to_acl_extended_rule_assignment_fail(self):
        """
        Test that Standard Access List cannot be assigned to ACLExtendedRule.
        """
        standard_acl1 = AccessList.objects.create(
            name="STANDARD_ACL",
            type=ACLTypeChoices.TYPE_STANDARD,
            default_action=self.default_action,
            comments="STANDARD_ACL",
        )
        extended_rule = ACLExtendedRule(
            access_list=standard_acl1,
            sequence=170,
            action="remark",
            remark="Test remark",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created rule with remark",
        )
        with self.assertRaises(ValidationError):
            extended_rule.full_clean()

    def test_duplicate_sequence_per_acl_fail(self):
        """
        Test that the rule sequence must be unique per AccessList.
        """
        params = {
            "access_list": self.extended_acl1,
            "sequence": 10,
            "action": "permit",
        }
        rule_1 = ACLExtendedRule(**params)
        rule_1.full_clean()
        rule_1.save()
        rule_2 = ACLExtendedRule(**params)
        with self.assertRaises(ValidationError):
            rule_2.full_clean()

    def test_acl_extended_rule_action_remark_with_no_remark_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and without remark fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="remark",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Invalid rule with action 'remark' and without remark",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_action_remark_with_source_prefix_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and source prefix fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="remark",
            remark="",
            source=self.prefix1,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Invalid rule with action 'remark' and source prefix",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_action_remark_with_source_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and source ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="remark",
            remark="",
            source=self.prefix1,
            source_port_ranges=string_to_ranges("80, 443"),
            destination=None,
            destination_port_ranges=None,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            description="Invalid rule with action 'remark' and source ports",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_action_remark_with_destination_prefix_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and destination prefix fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="remark",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=self.prefix1,
            destination_port_ranges=None,
            protocol=None,
            description="Invalid rule with action 'remark' and destination prefix",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_action_remark_with_destination_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and destination ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="remark",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=self.prefix1,
            destination_port_ranges=string_to_ranges("80, 443"),
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            description="Invalid rule with action 'remark' and destination ports",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_action_remark_with_protocol_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and protocol fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="remark",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            description="Invalid rule with action 'remark' and ICMP protocol",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_non_tcp_udp_protocols_reject_ports(self):
        """
        Test that ACLExtendedRule rejects ports on every protocol except TCP and UDP.
        """
        portless_protocols = [
            protocol
            for protocol in ACLProtocolChoices.values()
            if protocol not in {ACLProtocolChoices.PROTOCOL_TCP, ACLProtocolChoices.PROTOCOL_UDP}
        ]
        for new_protocol in ("gre", "eigrp", "ospf", "pim"):
            self.assertIn(new_protocol, portless_protocols)

        for protocol in portless_protocols:
            for field_name in ("source_port_ranges", "destination_port_ranges"):
                with self.subTest(protocol=protocol, field=field_name):
                    invalid_rule = ACLExtendedRule(
                        access_list=self.extended_acl1,
                        sequence=10,
                        action="permit",
                        remark="",
                        protocol=protocol,
                        description=f"Invalid rule with protocol '{protocol}' and {field_name} set",
                        **{field_name: string_to_ranges("80, 443")},
                    )
                    with self.assertRaises(ValidationError):
                        invalid_rule.full_clean()

    def test_acl_extended_rule_with_invalid_source_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with invalid source ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=string_to_ranges("0, 70000"),
            destination=None,
            destination_port_ranges=None,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            description="Invalid rule with invalid source ports",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_with_invalid_destination_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with invalid destination ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=string_to_ranges("1-65536"),
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            description="Invalid rule with invalid destination ports",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_invalid_aci_extended_rule_source_object(self):
        """
        Test ACLExtendedRule source object validation.
        """
        invalid_acl_rule_source_object = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="permit",
            remark="",
            source=self.device1,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            description="Rule with invalid source object.",
        )
        with self.assertRaises(ValidationError):
            invalid_acl_rule_source_object.full_clean()

    def test_invalid_aci_extended_rule_destination_object(self):
        """
        Test ACLExtendedRule destination object validation.
        """
        invalid_acl_rule_destination_object = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=self.device1,
            destination_port_ranges=None,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            description="Rule with invalid destination object.",
        )
        with self.assertRaises(ValidationError):
            invalid_acl_rule_destination_object.full_clean()

    def test_valid_acl_rule_action_choices(self):
        """
        Test ACLExtendedRule action choices using VALID choices.
        """
        valid_acl_rule_action_choices = ["deny", "permit", "remark"]

        for action_choice in valid_acl_rule_action_choices:
            valid_acl_rule_action = ACLExtendedRule(
                access_list=self.extended_acl1,
                sequence=10,
                action=action_choice,
                remark="Remark" if action_choice == "remark" else None,
                description=f"VALID ACL RULE ACTION CHOICES USED: action={action_choice}",
            )
            valid_acl_rule_action.full_clean()

    def test_invalid_acl_rule_action_choices(self):
        """
        Test ACLExtendedRule action choices using INVALID choices.
        """
        invalid_acl_rule_action_choice = "both"

        invalid_acl_rule_action = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action=invalid_acl_rule_action_choice,
            description=f"INVALID ACL RULE ACTION CHOICES USED: action={invalid_acl_rule_action_choice}",
        )

        with self.assertRaises(ValidationError):
            invalid_acl_rule_action.full_clean()

    def test_valid_acl_rule_protocol_choices(self):
        """
        Test ACLExtendedRule protocol choices using VALID choices.
        """
        valid_acl_rule_protocol_choices = ["icmp", "ip", "tcp", "udp", "gre", "eigrp", "ospf", "pim"]

        for protocol_choice in valid_acl_rule_protocol_choices:
            with self.subTest(protocol=protocol_choice):
                valid_acl_rule_protocol = ACLExtendedRule(
                    access_list=self.extended_acl1,
                    sequence=10,
                    action=self.default_action,
                    protocol=protocol_choice,
                    description=f"VALID ACL RULE PROTOCOL CHOICES USED: protocol={protocol_choice}",
                )
                valid_acl_rule_protocol.full_clean()

    def test_invalid_acl_rule_protocol_choices(self):
        """
        Test ACLExtendedRule protocol choices using INVALID choices.
        """
        invalid_acl_rule_protocol_choice = "ethernet"

        invalid_acl_rule_protocol = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            protocol=invalid_acl_rule_protocol_choice,
            description=f"INVALID ACL RULE PROTOCOL CHOICES USED: protocol={invalid_acl_rule_protocol_choice}",
        )

        with self.assertRaises(ValidationError):
            invalid_acl_rule_protocol.full_clean()

    def test_acl_extended_rule_family_v4_acl_rejects_v6_objects(self):
        """
        Test that IPv4 ACL must not accept rules carrying IPv6 objects.
        """
        acl_v4 = AccessList.objects.create(
            name="RF4",
            type=self.acl_type,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=self.default_action,
        )
        invalid_rule = ACLExtendedRule(
            access_list=acl_v4,
            sequence=10,
            action=ACLActionChoices.ACTION_PERMIT,
            source=self.prefix1_v6,
            destination=self.prefix1_v6,
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_family_v6_acl_rejects_v4_objects(self):
        """
        Test that IPv6 ACL must not accept rules carrying IPv4 objects.
        """
        acl = AccessList.objects.create(
            name="RF6",
            type=self.acl_type,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=self.default_action,
        )
        invalid_rule = ACLExtendedRule(
            access_list=acl,
            sequence=10,
            action=ACLActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            destination=self.prefix1_v6,
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_family_dual_forbids_mixing_families_within_one_rule(self):
        """
        Test that dual ACLs forbid mixing of IPv4 and IPv6 objects within one rule.
        """
        acl = AccessList.objects.create(
            name="RFD",
            type=self.acl_type,
            family=ACLFamilyChoices.FAMILY_DUAL,
            default_action=self.default_action,
        )
        mixed = ACLExtendedRule(
            access_list=acl,
            sequence=10,
            action=ACLActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            destination=self.prefix1_v6,
        )
        with self.assertRaises(ValidationError):
            mixed.full_clean()

    def test_acl_extended_rule_string_to_ranges(self):
        """
        Tests the conversion port ranges as strings to NumericRange objects.
        """
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action=ACLActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            source_port_ranges=string_to_ranges("1024-65535"),
            destination=None,
            destination_port_ranges=string_to_ranges("80, 443, 22-23"),
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
        )
        rule.clean()
        self.assertEqual(rule.source_port_ranges[0], NumericRange(1024, 65536, bounds="[)"))
        self.assertEqual(rule.destination_port_ranges[0], NumericRange(22, 24, bounds="[)"))
        self.assertEqual(rule.destination_port_ranges[1], NumericRange(80, 81, bounds="[)"))
        self.assertEqual(rule.destination_port_ranges[2], NumericRange(443, 444, bounds="[)"))

    def test_acl_extended_rule_port_ranges_are_canonicalized_and_collapsed(self):
        """
        Test that port ranges are canonicalized and collapsed.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=155,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=[
                NumericRange(23, 25, bounds="[]"),
                NumericRange(22, 22, bounds="[]"),
                NumericRange(80, 81, bounds="[]"),
            ],
            destination=self.prefix2,
            destination_port_ranges=[
                NumericRange(443, 443, bounds="[]"),
                NumericRange(444, 445, bounds="[]"),
            ],
            protocol=self.protocol,
            description="Created rule with canonicalized port ranges",
        )

        created_rule.full_clean()

        self.assertEqual(
            created_rule.source_port_ranges,
            [NumericRange(22, 26), NumericRange(80, 82)],
        )
        self.assertEqual(
            created_rule.destination_port_ranges,
            [NumericRange(443, 446)],
        )

    def test_acl_extended_rule_with_overlapping_source_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with overlapping source port ranges fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=156,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=[
                NumericRange(22, 24, bounds="[]"),
                NumericRange(24, 26, bounds="[]"),
            ],
            destination=None,
            destination_port_ranges=None,
            protocol=self.protocol,
            description="Invalid rule with overlapping source ports",
        )

        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_with_reversed_source_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with a reversed source port range fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=157,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=string_to_ranges("4-3"),
            destination=None,
            destination_port_ranges=None,
            protocol=self.protocol,
            description="Invalid rule with reversed source port range",
        )

        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_with_empty_half_open_source_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with an empty half-open source port range fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=158,
            action="permit",
            remark="",
            source=self.prefix1,
            source_port_ranges=[NumericRange(4, 4, bounds="[)")],
            destination=None,
            destination_port_ranges=None,
            protocol=self.protocol,
            description="Invalid rule with empty half-open source port range",
        )

        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_switching_the_destination_leaves_the_source_shadow_columns(self):
        """Test that the two roles are independent, so switching one leaves the other."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.extended_acl1,
            sequence=920,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            destination=self.aggregate1,
        )
        cached = self._cached_objects(rule)
        self.assertEqual(cached["_source_prefix"], self.prefix1.pk)
        self.assertEqual(cached["_destination_aggregate"], self.aggregate1.pk)

        rule.destination = self.ip_range1
        rule.save()

        cached = self._cached_objects(rule)
        self.assertEqual(cached["_source_prefix"], self.prefix1.pk)
        self.assertIsNone(cached["_destination_aggregate"])
        self.assertEqual(cached["_destination_iprange"], self.ip_range1.pk)

    @staticmethod
    def _cached_objects(rule):
        """Read the shadow columns back from the database, which is what the filters query."""
        return (
            ACLExtendedRule.objects.filter(pk=rule.pk)
            .values("_source_prefix", "_destination_aggregate", "_destination_iprange")
            .get()
        )

    def test_logging_defaults_to_disabled(self):
        """Test that a new rule logs nothing until asked to."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
        )
        self.assertFalse(rule.log_matches)
        self.assertEqual(rule.log_options, [])

    def test_log_options_require_log_matches(self):
        """Test that options are rejected while logging is disabled."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=30,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            log_matches=False,
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.full_clean()
        self.assertIn("log_options", ctx.exception.message_dict)

    def test_remark_rule_rejects_logging(self):
        """Test that a remark cannot request logging, since it matches nothing."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=40,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="Remark",
            log_matches=True,
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.full_clean()
        self.assertIn("log_matches", ctx.exception.message_dict)

    def test_remark_logging_errors_accumulate_with_other_remark_errors(self):
        """Test that a malformed remark reports every offending field at once."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=50,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="",
            log_matches=True,
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.full_clean()
        self.assertIn("remark", ctx.exception.message_dict)
        self.assertIn("log_matches", ctx.exception.message_dict)

    def test_log_matches_without_options_is_valid(self):
        """Test that enabling logging without naming a destination is allowed."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=70,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            log_matches=True,
        )
        rule.full_clean()

    def test_logging_defaults_persist_as_disabled(self):
        """Test that the stored default is disabled with no options."""
        rule = ACLExtendedRule.objects.create(
            access_list=self.extended_acl1,
            sequence=80,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
        )
        rule.refresh_from_db()
        self.assertFalse(rule.log_matches)
        self.assertEqual(rule.log_options, [])

    def test_clone_carries_the_logging_state(self):
        """Test that cloning reproduces the logging values, not just the field names."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=90,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            log_matches=True,
            log_options=[
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
                ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
            ],
        )
        rule.full_clean()
        rule.save()

        attrs = rule.clone()
        self.assertTrue(attrs["log_matches"])
        self.assertEqual(attrs["log_options"], ["cisco-log-input", "syslog"])

    def test_clone_carries_both_generic_references(self):
        """clone() must emit the subwidget keys the add form reads, for both roles."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=91,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            destination=self.prefix2,
        )
        rule.full_clean()
        rule.save()

        attrs = rule.clone()
        source_type = ContentType.objects.get_for_model(self.prefix1)
        destination_type = ContentType.objects.get_for_model(self.prefix2)
        self.assertEqual(attrs["source_content_type"], source_type.pk)
        self.assertEqual(attrs["source_object_id"], self.prefix1.pk)
        self.assertEqual(attrs["destination_content_type"], destination_type.pk)
        self.assertEqual(attrs["destination_object_id"], self.prefix2.pk)

    def test_unsupported_log_option_is_rejected(self):
        """Test that a value outside the choice set fails validation."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=95,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            log_matches=True,
            log_options=["not-a-real-option"],
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.full_clean()
        self.assertIn("log_options", ctx.exception.message_dict)

    def test_log_options_list_renders_display_values(self):
        """Test that the display helper resolves labels and passes through unknown values."""
        rule = ACLExtendedRule(
            log_options=["syslog", "vendor-x-future-option"],
        )
        self.assertEqual(
            rule.log_options_list,
            ["Syslog", "vendor-x-future-option"],
        )

    def test_log_options_badges_pair_labels_with_colors(self):
        """Test that the badge helper pairs each label with its color, leaving unknown values uncolored."""
        rule = ACLExtendedRule(
            log_options=["syslog", "vendor-x-future-option"],
        )
        self.assertEqual(
            rule.log_options_badges,
            [("Syslog", "blue"), ("vendor-x-future-option", None)],
        )

    def test_remark_rule_rejects_log_options(self):
        """Test that a remark reports the remark error rather than the master-switch one."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=45,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="Remark",
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.full_clean()
        self.assertEqual(
            ctx.exception.message_dict["log_options"],
            ["When the action is 'remark', Log options must not be set."],
        )

    def test_log_options_are_composable_and_canonicalized(self):
        """Test that options combine, deduplicate and reach the database sorted."""
        rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            sequence=20,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix1,
            log_matches=True,
            log_options=[
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
                ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
            ],
        )
        rule.full_clean()
        rule.save()
        rule.refresh_from_db()
        self.assertEqual(
            rule.log_options,
            [
                ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT,
                ACLRuleLogOptionChoices.OPTION_SYSLOG,
            ],
        )
