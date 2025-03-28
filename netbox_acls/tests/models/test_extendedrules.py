from django.core.exceptions import ValidationError

from netbox_acls.choices import ACLProtocolChoices, ACLTypeChoices
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
        cls.default_action = "deny"
        cls.protocol = ACLProtocolChoices.PROTOCOL_TCP

        # AccessLists
        cls.extended_acl1 = AccessList.objects.create(
            name="EXTENDED_ACL",
            assigned_object=cls.device1,
            type=cls.acl_type,
            default_action=cls.default_action,
            comments="EXTENDED_ACL",
        )
        cls.extended_acl2 = AccessList.objects.create(
            name="EXTENDED_ACL",
            assigned_object=cls.virtual_machine1,
            type=cls.acl_type,
            default_action=cls.default_action,
            comments="EXTENDED_ACL",
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
            source_prefix=None,
            source_ports=None,
            destination_prefix=None,
            destination_ports=None,
            protocol=None,
            description=(
                "Created rule with any source prefix, any source port, "
                "any destination prefix, any destination port, and any protocol."
            ),
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.index, 10)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, None)
        self.assertEqual(created_rule.source_ports, None)
        self.assertEqual(created_rule.destination_prefix, None)
        self.assertEqual(created_rule.destination_ports, None)
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(
            created_rule.description,
            (
                "Created rule with any source prefix, any source port, "
                "any destination prefix, any destination port, and any protocol."
            ),
        )
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_source_prefix_creation_success(self):
        """
        Test that ACLExtendedRule with source prefix creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=20,
            action="permit",
            remark="",
            source_prefix=self.prefix1,
            source_ports=None,
            destination_prefix=None,
            destination_ports=None,
            protocol=None,
            description="Created rule with source prefix",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.index, 20)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, self.prefix1)
        self.assertEqual(created_rule.source_ports, None)
        self.assertEqual(created_rule.destination_prefix, None)
        self.assertEqual(created_rule.destination_ports, None)
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with source prefix")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_source_ports_creation_success(self):
        """
        Test that ACLExtendedRule with source ports creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=30,
            action="permit",
            remark="",
            source_prefix=self.prefix1,
            source_ports=[22, 443],
            destination_prefix=None,
            destination_ports=None,
            protocol=self.protocol,
            description="Created rule with source ports",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.index, 30)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, self.prefix1)
        self.assertEqual(created_rule.source_ports, [22, 443])
        self.assertEqual(created_rule.destination_prefix, None)
        self.assertEqual(created_rule.destination_ports, None)
        self.assertEqual(created_rule.protocol, self.protocol)
        self.assertEqual(created_rule.description, "Created rule with source ports")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_destination_prefix_creation_success(self):
        """
        Test that ACLExtendedRule with destination prefix creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=40,
            action="permit",
            remark="",
            source_prefix=None,
            source_ports=None,
            destination_prefix=self.prefix1,
            destination_ports=None,
            protocol=None,
            description="Created rule with destination prefix",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.index, 40)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, None)
        self.assertEqual(created_rule.source_ports, None)
        self.assertEqual(created_rule.destination_prefix, self.prefix1)
        self.assertEqual(created_rule.destination_ports, None)
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with destination prefix")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_destination_ports_creation_success(self):
        """
        Test that ACLExtendedRule with destination ports creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=50,
            action="permit",
            remark="",
            source_prefix=None,
            source_ports=None,
            destination_prefix=self.prefix1,
            destination_ports=[22, 443],
            protocol=self.protocol,
            description="Created rule with destination ports",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.index, 50)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, None)
        self.assertEqual(created_rule.source_ports, None)
        self.assertEqual(created_rule.destination_prefix, self.prefix1)
        self.assertEqual(created_rule.destination_ports, [22, 443])
        self.assertEqual(created_rule.protocol, self.protocol)
        self.assertEqual(created_rule.description, "Created rule with destination ports")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_acl_extended_rule_icmp_protocol_creation_success(self):
        """
        Test that ACLExtendedRule with ICMP protocol creation passes validation.
        """
        created_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=60,
            action="permit",
            remark="",
            source_prefix=self.prefix1,
            source_ports=None,
            destination_prefix=self.prefix2,
            destination_ports=None,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            description="Created rule with ICMP protocol",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.index, 60)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, self.prefix1)
        self.assertEqual(created_rule.source_ports, None)
        self.assertEqual(created_rule.destination_prefix, self.prefix2)
        self.assertEqual(created_rule.destination_ports, None)
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
            index=70,
            action="permit",
            remark="",
            source_prefix=self.prefix1,
            source_ports=[4000, 5000],
            destination_prefix=self.prefix2,
            destination_ports=[22, 443],
            protocol=self.protocol,
            description="Created rule with complete parameters",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.index, 70)
        self.assertEqual(created_rule.action, "permit")
        self.assertEqual(created_rule.remark, "")
        self.assertEqual(created_rule.source_prefix, self.prefix1)
        self.assertEqual(created_rule.source_ports, [4000, 5000])
        self.assertEqual(created_rule.destination_prefix, self.prefix2)
        self.assertEqual(created_rule.destination_ports, [22, 443])
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
            index=80,
            action="remark",
            remark="Test remark",
            source_prefix=None,
            source_ports=None,
            destination_prefix=None,
            destination_ports=None,
            protocol=None,
            description="Created rule with remark",
        )
        created_rule.full_clean()

        self.assertTrue(isinstance(created_rule, ACLExtendedRule), True)
        self.assertEqual(created_rule.index, 80)
        self.assertEqual(created_rule.action, "remark")
        self.assertEqual(created_rule.remark, "Test remark")
        self.assertEqual(created_rule.source_prefix, None)
        self.assertEqual(created_rule.source_ports, None)
        self.assertEqual(created_rule.destination_prefix, None)
        self.assertEqual(created_rule.destination_ports, None)
        self.assertEqual(created_rule.protocol, None)
        self.assertEqual(created_rule.description, "Created rule with remark")
        self.assertEqual(isinstance(created_rule.access_list, AccessList), True)
        self.assertEqual(created_rule.access_list.type, self.acl_type)

    def test_access_list_standard_to_acl_extended_rule_assignment_fail(self):
        """
        Test that Standard Access List cannot be assigned to ACLExtendedRule.
        """
        standard_acl1 = AccessList.objects.create(
            name="STANDARD_ACL",
            assigned_object=self.device1,
            type=ACLTypeChoices.TYPE_STANDARD,
            default_action=self.default_action,
            comments="STANDARD_ACL",
        )
        extended_rule = ACLExtendedRule(
            access_list=standard_acl1,
            index=80,
            action="remark",
            remark="Test remark",
            source_prefix=None,
            source_ports=None,
            destination_prefix=None,
            destination_ports=None,
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

    def test_acl_extended_rule_action_permit_with_remark_fail(self):
        """
        Test that ACLExtendedRule with action 'permit' and remark fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=10,
            action="permit",
            remark="Remark",
            source_prefix=None,
            source_ports=None,
            destination_prefix=None,
            destination_ports=None,
            protocol=None,
            description="Invalid rule with action 'permit' and remark",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_action_remark_with_no_remark_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and without remark fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=10,
            action="remark",
            remark="",
            source_prefix=None,
            source_ports=None,
            destination_prefix=None,
            destination_ports=None,
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
            source_prefix=self.prefix1,
            source_ports=None,
            destination_prefix=None,
            destination_ports=None,
            protocol=None,
            description="Invalid rule with action 'remark' and source prefix",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_action_remark_with_source_ports_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and source ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=10,
            action="remark",
            remark="",
            source_prefix=self.prefix1,
            source_ports=[80, 443],
            destination_prefix=None,
            destination_ports=None,
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
            source_prefix=None,
            source_ports=None,
            destination_prefix=self.prefix1,
            destination_ports=None,
            protocol=None,
            description="Invalid rule with action 'remark' and destination prefix",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

    def test_acl_extended_rule_action_remark_with_destination_ports_fail(self):
        """
        Test that ACLExtendedRule with action 'remark' and destination ports fails validation.
        """
        invalid_rule = ACLExtendedRule(
            access_list=self.extended_acl1,
            index=10,
            action="remark",
            remark="",
            source_prefix=None,
            source_ports=None,
            destination_prefix=self.prefix1,
            destination_ports=[80, 443],
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
            source_prefix=None,
            source_ports=None,
            destination_prefix=None,
            destination_ports=None,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            description="Invalid rule with action 'remark' and ICMP protocol",
        )
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()

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
        valid_acl_rule_protocol_choices = ["icmp", "tcp", "udp"]

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
