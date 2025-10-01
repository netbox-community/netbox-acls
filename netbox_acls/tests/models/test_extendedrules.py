from django.core.exceptions import ValidationError
from django.db.backends.postgresql.psycopg_any import NumericRange
from utilities.data import string_to_ranges

from netbox_acls.choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLTypeChoices,
)
from netbox_acls.models import AccessList, ACLExtendedRule

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
            index=10,
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
        self.assertEqual(created_rule.index, 10)
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
            index=20,
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
        self.assertEqual(created_rule.index, 20)
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
            index=30,
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
        self.assertEqual(created_rule.index, 30)
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
            index=40,
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
        self.assertEqual(created_rule.index, 40)
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
            index=50,
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
        self.assertEqual(created_rule.index, 50)
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
            index=70,
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
        self.assertEqual(created_rule.index, 70)
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
            index=80,
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
        self.assertEqual(created_rule.index, 80)
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
            index=90,
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
        self.assertEqual(created_rule.index, 90)
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
            index=100,
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
        self.assertEqual(created_rule.index, 100)
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
            index=110,
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
        self.assertEqual(created_rule.index, 110)
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
            index=130,
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
        self.assertEqual(created_rule.index, 130)
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
            index=140,
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
        self.assertEqual(created_rule.index, 140)
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
            index=140,
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
        self.assertEqual(created_rule.index, 140)
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

    def test_acl_extended_rule_complete_params_creation_success(self):
        """
        Test that ACLExtendedRule with complete parameters creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=150,
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
        self.assertEqual(created_rule.index, 150)
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
            index=160,
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
        self.assertEqual(created_rule.index, 160)
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
            index=120,
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
        self.assertEqual(created_rule.index, 120)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "Inline remark")
        self.assertEqual(created_rule.description, "Created permit rule with remark")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_action_permit_with_shared_index_action_remark_success(self):
        """
        Test that ACLExtendedRule with action 'permit' and action 'remark' shared index passes validation.
        """
        created_permit_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=130,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=self.protocol,
            description="Created permit rule with same index as remark",
        )
        created_permit_rule.full_clean()
        created_permit_rule.save()

        created_remark_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=130,
            action="remark",
            remark="Standalone remark",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=None,
            protocol=None,
            description="Created remark rule with same index as permit rule",
        )
        created_remark_rule.full_clean()

        self.assertTrue(isinstance(created_remark_rule, ACLExtendedRule), True)
        self.assertEqual(created_remark_rule.index, 130)
        self.assertEqual(created_remark_rule.action, "remark")
        self.assertEqual(created_remark_rule.remark, "Standalone remark")
        self.assertEqual(created_remark_rule.description, "Created remark rule with same index as permit rule")
        self.assertEqual(isinstance(created_remark_rule.access_list, AccessList), True)
        self.assertEqual(created_remark_rule.access_list.type, self.acl_type)

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
            index=170,
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

    def test_duplicate_index_per_acl_fail(self):
        """
        Test that the rule index must be unique per AccessList.
        """
        params = {
            "access_list": self.extended_acl1,
            "index": 10,
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
            index=10,
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
            index=10,
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
            index=10,
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
            index=10,
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
            index=10,
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
            index=10,
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

    def test_acl_extended_rule_protocol_ip_with_source_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with protocol 'ip' and source ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=10,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=string_to_ranges("80, 443"),
            destination=None,
            destination_port_ranges=None,
            protocol=ACLProtocolChoices.PROTOCOL_IP,
            description="Invalid rule with protocol 'ip' and source ports set",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_protocol_icmp_with_destination_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with protocol 'icmp' and destination ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=10,
            action="permit",
            remark="",
            source=None,
            source_port_ranges=None,
            destination=None,
            destination_port_ranges=string_to_ranges("80, 443"),
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            description="Invalid rule with protocol 'icmp' and destination ports set",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_with_invalid_source_port_ranges_fail(self):
        """
        Test that ACLExtendedRule with invalid source ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=10,
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
            index=10,
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
            index=10,
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
            index=10,
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
                index=10,
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
            index=10,
            action=invalid_acl_rule_action_choice,
            description=f"INVALID ACL RULE ACTION CHOICES USED: action={invalid_acl_rule_action_choice}",
        )

        with self.assertRaises(ValidationError):
            invalid_acl_rule_action.full_clean()

    def test_valid_acl_rule_protocol_choices(self):
        """
        Test ACLExtendedRule protocol choices using VALID choices.
        """
        valid_acl_rule_protocol_choices = ["icmp", "ip", "tcp", "udp"]

        for protocol_choice in valid_acl_rule_protocol_choices:
            valid_acl_rule_protocol = ACLExtendedRule(
                access_list=self.extended_acl1,
                index=10,
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
            index=10,
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
            index=10,
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
            index=10,
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
            index=10,
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
            index=10,
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
            index=155,
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
            index=156,
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
            index=157,
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
            index=158,
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
