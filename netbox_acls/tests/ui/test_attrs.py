"""Unit tests for the plugin's object attribute classes."""

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from dcim.models import Device, Interface
from virtualization.models import VirtualMachine, VMInterface

from ...choices import ACLRuleActionChoices, ACLTypeChoices
from ...models import AccessList, ACLStandardRule
from ...ui.attrs import AssignedObjectAttr, LogOptionsAttr, RuleCountAttr


class AssignedObjectAttrTestCase(SimpleTestCase):
    """Test the assigned object attribute."""

    def test_context_carries_the_target_parent(self):
        """Test that an interface target is prefixed with its own parent."""
        device = Device(name="Device 1")
        virtual_machine = VirtualMachine(name="VM 1")

        for target, expected in (
            (Interface(name="eth0", device=device), device),
            (VMInterface(name="eth0", virtual_machine=virtual_machine), virtual_machine),
            # A host target is its own parent, so the prefix is dropped.
            (device, None),
        ):
            with self.subTest(target=type(target).__name__):
                context = AssignedObjectAttr("assigned_object").get_context(
                    None,
                    "assigned_object",
                    target,
                    {},
                )

                self.assertEqual(context["parent"], expected)
                self.assertEqual(context["content_type"], type(target)._meta.verbose_name)


class LogOptionsAttrTestCase(TestCase):
    """Test the log options attribute."""

    def test_empty_log_options_resolve_to_none(self):
        """Test that a rule with no log options renders the placeholder."""
        rule = ACLStandardRule(log_options=[])
        self.assertIsNone(LogOptionsAttr("log_options_badges").get_value(rule))

    def test_stored_log_options_render_as_badges(self):
        """Test that each stored log option renders as its colored badge."""
        rule = ACLStandardRule(log_options=["syslog", "cisco-log-input"])

        rendered = LogOptionsAttr("log_options_badges").render(rule, {"name": "log_options"})

        self.assertInHTML('<span class="badge text-bg-blue">Syslog</span>', rendered)
        self.assertInHTML('<span class="badge text-bg-purple">Log-input</span>', rendered)


class RuleCountAttrTestCase(TestCase):
    """Test the rule count attribute."""

    @classmethod
    def setUpTestData(cls):
        """Create a standard access list carrying a single rule."""
        cls.access_list = AccessList.objects.create(
            name="testacl",
            type=ACLTypeChoices.TYPE_STANDARD,
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
        )

    def test_counts_the_rules_of_the_matching_type(self):
        """Test that the count comes from the relation matching the ACL type."""
        self.assertEqual(RuleCountAttr().get_value(self.access_list), 1)

    def test_links_to_the_filtered_rule_list(self):
        """Test that the count links to the rule list filtered by this ACL."""
        context = RuleCountAttr().get_context(self.access_list, "rules", 1, {})

        expected = reverse("plugins:netbox_acls:aclstandardrule_list")
        self.assertEqual(context["url"], f"{expected}?access_list_id={self.access_list.pk}")
