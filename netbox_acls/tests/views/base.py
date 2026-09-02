"""
Shared bases and fixtures for the plugin's view tests.
"""

from netaddr import IPNetwork

from ipam.models import RIR, Aggregate, IPAddress, IPRange, Prefix

__all__ = (
    "ACLRuleSequenceTestsMixin",
    "PluginViewTestCase",
    "build_ipam_objects",
)


class PluginViewTestCase:
    """
    Resolve plugin view URLs.

    The shared helper builds "<app_label>:<model>_<action>" and omits the
    "plugins" namespace every plugin URL is registered under.
    """

    def _get_base_url(self):
        return f"plugins:{super()._get_base_url()}"


class ACLRuleSequenceTestsMixin:
    """
    Cover the automatic sequence assignment on a rule's add and edit views.

    The host test case must declare ``add_permission`` and ``change_permission``. These
    tests grant them one at a time rather than through ``user_permissions``, which is
    granted in ``setUp``: the inherited ``test_*_without_permission`` cases assert a 403,
    and a standing add or change permission turns that into a 200.

    Both rule fixtures seed sequences 10 through 50, so the next one is 60. The mixin is a
    plain class, not a test case, so the runner never collects it on its own.
    """

    add_permission = None
    change_permission = None
    expected_next_sequence = 60

    def _get_form(self, action, permission, instance=None, query=""):
        self.add_permissions(permission)
        response = self.client.get(f"{self._get_url(action, instance)}{query}")
        self.assertHttpStatus(response, 200)
        return response.context["form"]

    def test_sequence_prefilled_from_access_list(self):
        """Test that the add form pre-populates and displays the next sequence."""
        form = self._get_form(
            "add",
            self.add_permission,
            query=f"?access_list={self.access_list.pk}",
        )
        self.assertEqual(form.instance.sequence, self.expected_next_sequence)
        self.assertEqual(form["sequence"].value(), self.expected_next_sequence)

    def test_explicit_sequence_is_preserved(self):
        """Test that a supplied sequence reaches the form instead of being replaced."""
        form = self._get_form(
            "add",
            self.add_permission,
            query=f"?access_list={self.access_list.pk}&sequence=99",
        )
        self.assertIsNone(form.instance.sequence)
        # normalize_querydict yields strings, and initial wins over the instance.
        self.assertEqual(form["sequence"].value(), "99")

    def test_sequence_not_assigned_without_access_list(self):
        """Test that adding a rule with no access list chosen leaves the sequence empty."""
        form = self._get_form("add", self.add_permission)
        self.assertIsNone(form.instance.sequence)

    def test_malformed_access_list_is_ignored(self):
        """Test that a malformed access list id is ignored rather than raising."""
        # str.isdigit() is true for the superscript and the 5000-digit string, and int()
        # rejects both.
        for value in ("notanumber", "²", "9" * 5000):
            with self.subTest(value=value):
                form = self._get_form("add", self.add_permission, query=f"?access_list={value}")
                self.assertIsNone(form.instance.sequence)

    def test_sequence_untouched_when_editing(self):
        """Test that editing an existing rule does not recompute its sequence."""
        rule = self.model.objects.filter(access_list=self.access_list).earliest("sequence")
        form = self._get_form("edit", self.change_permission, instance=rule)
        self.assertEqual(form.instance.sequence, rule.sequence)


def build_ipam_objects():
    """Create one of each source and destination type an ACL rule accepts."""
    rir = RIR.objects.create(name="RIR 1", slug="rir-1")
    aggregate = Aggregate.objects.create(prefix=IPNetwork("10.0.0.0/8"), rir=rir)
    prefix = Prefix.objects.create(prefix=IPNetwork("10.1.0.0/16"))
    ip_address = IPAddress.objects.create(address=IPNetwork("10.0.0.1/24"))
    ip_range = IPRange.objects.create(
        start_address=IPNetwork("10.0.1.1/24"),
        end_address=IPNetwork("10.0.1.254/24"),
    )
    return aggregate, prefix, ip_address, ip_range
