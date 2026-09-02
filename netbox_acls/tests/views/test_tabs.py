"""
Tests for the ACL tabs contributed to plugin and core objects.

These views sit outside every standard NetBox test base, so nothing else reaches them.
"""

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import urlencode
from netaddr import IPNetwork

from dcim.choices import InterfaceTypeChoices
from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Manufacturer,
    Site,
    VirtualChassis,
)
from ipam.models import RIR, Aggregate, IPAddress, IPRange, Prefix
from utilities.testing import TestCase
from virtualization.models import Cluster, ClusterType, VirtualMachine

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLRuleUsageChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule
from ...views import (
    AccessListACLAssignmentView,
    ACLExtendedRuleChildrenView,
    ACLStandardRuleChildrenView,
    DeviceACLAssignmentView,
    InterfaceACLAssignmentView,
    VirtualChassisACLAssignmentView,
    VirtualMachineACLAssignmentView,
    VMInterfaceACLAssignmentView,
    rule_reference_filter,
)


class ACLAssignmentTabTestCase(TestCase):
    """Each assignment tab lists its own parent's assignments and nothing else."""

    # add_accesslist is withheld: its absence is what the access list tab's button pins.
    user_permissions = (
        "netbox_acls.view_aclassignment",
        "netbox_acls.add_aclassignment",
        "netbox_acls.view_accesslist",
        "dcim.view_device",
        "dcim.view_interface",
        "dcim.view_virtualchassis",
        "virtualization.view_virtualmachine",
        "virtualization.view_vminterface",
    )

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Device Type 1")
        role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        cls.device = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=device_type,
            role=role,
        )
        cls.interface = cls.device.interfaces.create(
            name="eth0",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.virtual_chassis = VirtualChassis.objects.create(name="Virtual Chassis 1")

        cluster_type = ClusterType.objects.create(name="Cluster Type 1", slug="cluster-type-1")
        cluster = Cluster.objects.create(name="Cluster 1", type=cluster_type)
        cls.virtual_machine = VirtualMachine.objects.create(name="VM 1", cluster=cluster)
        cls.vminterface = cls.virtual_machine.interfaces.create(name="eth0")

        # A second of every assignable object, so each tab has a same-model sibling to
        # exclude. Without one, a tab filtering only by content type, or not filtering at
        # all, returns the same single row as a correct one.
        cls.device2 = Device.objects.create(
            name="Device 2",
            site=site,
            device_type=device_type,
            role=role,
        )
        cls.interface2 = cls.device2.interfaces.create(
            name="eth0",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.virtual_chassis2 = VirtualChassis.objects.create(name="Virtual Chassis 2")
        cls.virtual_machine2 = VirtualMachine.objects.create(name="VM 2", cluster=cluster)
        cls.vminterface2 = cls.virtual_machine2.interfaces.create(name="eth0")

        cls.access_list = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        # A second access list, so the access list tab has assignments to exclude too.
        cls.access_list2 = AccessList.objects.create(
            name="testacl2",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        cls.assignments = cls.build_assignments(
            cls.access_list,
            (cls.device, cls.interface, cls.virtual_chassis, cls.virtual_machine, cls.vminterface),
        )
        cls.other_assignments = cls.build_assignments(
            cls.access_list2,
            (
                cls.device2,
                cls.interface2,
                cls.virtual_chassis2,
                cls.virtual_machine2,
                cls.vminterface2,
            ),
        )

    @staticmethod
    def build_assignments(access_list, targets):
        """Attach the access list to one of each assignable target type."""
        device, interface, virtual_chassis, virtual_machine, vminterface = targets
        assignments = {}
        for key, target, direction in (
            ("device", device, ACLAssignmentDirectionChoices.DIRECTION_NONE),
            ("interface", interface, ACLAssignmentDirectionChoices.DIRECTION_INGRESS),
            ("virtual_chassis", virtual_chassis, ACLAssignmentDirectionChoices.DIRECTION_NONE),
            ("virtual_machine", virtual_machine, ACLAssignmentDirectionChoices.DIRECTION_NONE),
            ("vminterface", vminterface, ACLAssignmentDirectionChoices.DIRECTION_EGRESS),
        ):
            assignments[key] = ACLAssignment.objects.create(
                access_list=access_list,
                direction=direction,
                assigned_object_type=ContentType.objects.get_for_model(target),
                assigned_object_id=target.pk,
            )
        return assignments

    def tab_cases(self):
        """
        Yield (view class, url name, parent, expected assignments) for every tab.

        Only the access list tab lives under the plugins namespace. The other five are
        registered against core models and resolve under dcim and virtualization.
        """
        return (
            (
                DeviceACLAssignmentView,
                "dcim:device_aclassignments",
                self.device,
                [self.assignments["device"]],
            ),
            (
                InterfaceACLAssignmentView,
                "dcim:interface_aclassignments",
                self.interface,
                [self.assignments["interface"]],
            ),
            (
                VirtualChassisACLAssignmentView,
                "dcim:virtualchassis_aclassignments",
                self.virtual_chassis,
                [self.assignments["virtual_chassis"]],
            ),
            (
                VirtualMachineACLAssignmentView,
                "virtualization:virtualmachine_aclassignments",
                self.virtual_machine,
                [self.assignments["virtual_machine"]],
            ),
            (
                VMInterfaceACLAssignmentView,
                "virtualization:vminterface_aclassignments",
                self.vminterface,
                [self.assignments["vminterface"]],
            ),
            (
                AccessListACLAssignmentView,
                "plugins:netbox_acls:accesslist_aclassignments",
                self.access_list,
                list(self.assignments.values()),
            ),
            (
                AccessListACLAssignmentView,
                "plugins:netbox_acls:accesslist_aclassignments",
                self.access_list2,
                list(self.other_assignments.values()),
            ),
        )

    def test_tab_lists_only_its_own_assignments(self):
        """Test that each tab narrows its children to the parent it hangs off."""
        for _view_class, url_name, parent, expected in self.tab_cases():
            with self.subTest(view=url_name, parent=parent):
                response = self.client.get(reverse(url_name, kwargs={"pk": parent.pk}))
                self.assertHttpStatus(response, 200)
                self.assertEqual(
                    {row.pk for row in response.context["table"].data},
                    {assignment.pk for assignment in expected},
                )

    def test_tab_badge_counts_the_assignments(self):
        """Test that the tab badge callback reports what the tab lists."""
        for view_class, url_name, parent, expected in self.tab_cases():
            with self.subTest(view=url_name, parent=parent):
                rendered = view_class.tab.render(parent)
                self.assertIsNotNone(rendered)
                self.assertEqual(rendered["badge"], len(expected))

    def test_add_link_carries_the_generic_object_params(self):
        """Test the link uses the subwidget names the assignment form reads."""
        for _view_class, url_name, parent, _expected in self.tab_cases():
            # The access list tab prefills access_list instead, so it carries
            # neither generic object parameter.
            if url_name.startswith("plugins:netbox_acls:accesslist"):
                continue
            with self.subTest(view=url_name, parent=parent):
                response = self.client.get(reverse(url_name, kwargs={"pk": parent.pk}))
                self.assertHttpStatus(response, 200)
                content_type = ContentType.objects.get_for_model(parent)
                self.assertContains(response, f"assigned_object_object_id={parent.pk}")
                self.assertContains(response, f"assigned_object_content_type={content_type.pk}")

    def test_access_list_tab_offers_its_add_link(self):
        """Test the access list tab prefills the link with the access list.

        The generic-object assertion above skips this tab, which is how its
        permission gate went unnoticed since it shipped.
        """
        add_url = reverse("plugins:netbox_acls:aclassignment_add")

        response = self.client.get(
            reverse("plugins:netbox_acls:accesslist_aclassignments", kwargs={"pk": self.access_list.pk})
        )

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Assign an ACL")
        self.assertContains(response, f'href="{add_url}?access_list={self.access_list.pk}')

    @staticmethod
    def add_link_href(parent, tab_url):
        """Return the add link the parent's action is expected to render."""
        if isinstance(parent, AccessList):
            params = {"access_list": parent.pk}
        else:
            params = {
                "assigned_object_content_type": ContentType.objects.get_for_model(parent).pk,
                "assigned_object_object_id": parent.pk,
            }
        params["return_url"] = tab_url
        add_url = reverse("plugins:netbox_acls:aclassignment_add")
        return escape(f"{add_url}?{urlencode(params)}")

    def test_add_link_returns_to_the_tab_it_was_clicked_from(self):
        """Test the return URL is the tab, not the parent's detail page.

        No parent page lists its assignments, so returning there hides the
        object the user just created. The whole href is asserted because the
        table config control emits a bare return_url for the same path.
        """
        for _view_class, url_name, parent, _expected in self.tab_cases():
            with self.subTest(view=url_name, parent=parent):
                url = reverse(url_name, kwargs={"pk": parent.pk})
                response = self.client.get(url)

                self.assertHttpStatus(response, 200)
                self.assertContains(response, f'href="{self.add_link_href(parent, url)}"')

    def test_every_tab_add_link_targets_the_assignment_form(self):
        """Test all six tabs link to the ACL assignment form.

        The permission is resolved against the view's child model, so a link
        to another model checks one permission and creates another object.
        """
        add_url = reverse("plugins:netbox_acls:aclassignment_add")

        for _view_class, url_name, parent, _expected in self.tab_cases():
            with self.subTest(view=url_name, parent=parent):
                response = self.client.get(reverse(url_name, kwargs={"pk": parent.pk}))

                self.assertHttpStatus(response, 200)
                self.assertContains(response, f'href="{add_url}?')

    def test_add_link_omits_a_return_url_the_view_does_not_provide(self):
        """Test the action tolerates a context carrying no return URL.

        Only a children view puts one there, so an unguarded lookup raises
        KeyError anywhere else. Core guards the same lookup.
        """
        action = AccessListACLAssignmentView.actions[0]

        params = action.get_url_params({"object": self.access_list})

        self.assertEqual(params["access_list"], self.access_list.pk)
        self.assertNotIn("return_url", params)

    def test_add_link_survives_a_filtered_tab(self):
        """Test a filtered tab does not leak its filters into the add form.

        return_url is request.get_full_path(), so it carries the tab's own
        query string. Written raw it splits at the first &, truncating the
        return URL and turning the rest into parameters of the add form.
        """
        url = reverse("dcim:device_aclassignments", kwargs={"pk": self.device.pk})
        tab_url = f"{url}?direction=none&q=foo"

        response = self.client.get(tab_url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, f'href="{self.add_link_href(self.device, tab_url)}"')


class ACLAssignmentTabAddPermissionTestCase(TestCase):
    """The add link follows the permission of the object it creates."""

    user_permissions = (
        "netbox_acls.view_aclassignment",
        "netbox_acls.view_accesslist",
        "netbox_acls.add_accesslist",
        "dcim.view_device",
    )

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Device Type 1")
        role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        cls.device = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=device_type,
            role=role,
        )
        cls.access_list = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

    def test_no_add_link_without_the_assignment_permission(self):
        """Test add_accesslist alone offers no link on either kind of tab.

        The access list tab used to gate on add_accesslist while its link
        created an ACLAssignment, so this user got a button leading to a form
        they could not submit.
        """
        cases = (
            ("plugins:netbox_acls:accesslist_aclassignments", self.access_list),
            ("dcim:device_aclassignments", self.device),
        )
        for url_name, parent in cases:
            with self.subTest(view=url_name, parent=parent):
                response = self.client.get(reverse(url_name, kwargs={"pk": parent.pk}))

                self.assertHttpStatus(response, 200)
                self.assertNotContains(response, "Assign an ACL")


class ACLRuleTabFixtureMixin:
    """
    Shared fixture for the IPAM rule tabs.

    A plain class, not a test case, so the runner never collects it on its own and the
    host cases can differ only in the permissions they grant.
    """

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name="RIR 1", slug="rir-1")
        cls.aggregate = Aggregate.objects.create(prefix=IPNetwork("10.0.0.0/8"), rir=rir)
        cls.prefix = Prefix.objects.create(prefix=IPNetwork("10.1.0.0/16"))
        cls.ip_address = IPAddress.objects.create(address=IPNetwork("10.2.0.1/24"))
        cls.ip_range = IPRange.objects.create(
            start_address=IPNetwork("10.3.0.1/24"),
            end_address=IPNetwork("10.3.0.254/24"),
        )

        # A same-model sibling carrying its own rules. Without one, a tab filtering only
        # by content type, or not filtering at all, returns the same single row as a
        # correct one.
        cls.other_prefix = Prefix.objects.create(prefix=IPNetwork("10.4.0.0/16"))
        # Referenced by nothing, so both of its tabs must hide themselves.
        cls.unused_prefix = Prefix.objects.create(prefix=IPNetwork("10.5.0.0/16"))

        cls.standard_acl = AccessList.objects.create(
            name="teststandardacl",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        cls.extended_acl = AccessList.objects.create(
            name="testextendedacl",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        targets = (cls.aggregate, cls.ip_address, cls.ip_range, cls.prefix, cls.other_prefix)

        # One rule per target, so every tab under test has a row of its own and a
        # same-model neighbour to exclude.
        cls.standard_rules = {
            target: ACLStandardRule.objects.create(
                access_list=cls.standard_acl,
                sequence=(index + 1) * 10,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=target,
            )
            for index, target in enumerate(targets)
        }
        # A second rule on one target, so a badge hardcoded to 1 cannot pass.
        cls.standard_second_prefix_rule = ACLStandardRule.objects.create(
            access_list=cls.standard_acl,
            sequence=60,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=cls.prefix,
        )
        cls.extended_sources = {
            target: ACLExtendedRule.objects.create(
                access_list=cls.extended_acl,
                sequence=(index + 1) * 10,
                action=ACLRuleActionChoices.ACTION_PERMIT,
                source=target,
            )
            for index, target in enumerate(targets)
        }
        cls.extended_destination = ACLExtendedRule.objects.create(
            access_list=cls.extended_acl,
            sequence=100,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=cls.other_prefix,
            destination=cls.prefix,
        )
        cls.extended_both = ACLExtendedRule.objects.create(
            access_list=cls.extended_acl,
            sequence=110,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=cls.prefix,
            destination=cls.prefix,
        )

    def standard_tab_cases(self):
        """Yield (url name, parent, expected rules) for every standard rule tab."""
        return (
            ("ipam:aggregate_aclstandardrules", self.aggregate, [self.standard_rules[self.aggregate]]),
            ("ipam:ipaddress_aclstandardrules", self.ip_address, [self.standard_rules[self.ip_address]]),
            ("ipam:iprange_aclstandardrules", self.ip_range, [self.standard_rules[self.ip_range]]),
            (
                "ipam:prefix_aclstandardrules",
                self.prefix,
                [self.standard_rules[self.prefix], self.standard_second_prefix_rule],
            ),
            ("ipam:prefix_aclstandardrules", self.other_prefix, [self.standard_rules[self.other_prefix]]),
        )

    def extended_tab_cases(self):
        """Yield (url name, parent, expected rules) for every extended rule tab."""
        return (
            ("ipam:aggregate_aclextendedrules", self.aggregate, [self.extended_sources[self.aggregate]]),
            ("ipam:ipaddress_aclextendedrules", self.ip_address, [self.extended_sources[self.ip_address]]),
            ("ipam:iprange_aclextendedrules", self.ip_range, [self.extended_sources[self.ip_range]]),
            (
                "ipam:prefix_aclextendedrules",
                self.prefix,
                [self.extended_sources[self.prefix], self.extended_destination, self.extended_both],
            ),
            (
                "ipam:prefix_aclextendedrules",
                self.other_prefix,
                [self.extended_sources[self.other_prefix], self.extended_destination],
            ),
        )


class ACLRuleTabTestCase(ACLRuleTabFixtureMixin, TestCase):
    """Each IPAM rule tab lists only the rules that reference its own parent."""

    user_permissions = (
        "netbox_acls.view_accesslist",
        "netbox_acls.view_aclstandardrule",
        "netbox_acls.view_aclextendedrule",
        "ipam.view_aggregate",
        "ipam.view_ipaddress",
        "ipam.view_iprange",
        "ipam.view_prefix",
    )

    def test_standard_tab_lists_only_referencing_rules(self):
        """Test that each standard rule tab narrows its children to its own parent."""
        for url_name, parent, expected in self.standard_tab_cases():
            with self.subTest(view=url_name, parent=parent):
                response = self.client.get(reverse(url_name, kwargs={"pk": parent.pk}))
                self.assertHttpStatus(response, 200)
                self.assertEqual(
                    {row.pk for row in response.context["table"].data},
                    {rule.pk for rule in expected},
                )

    def test_standard_tab_hides_the_source_columns(self):
        """Test that the columns holding the parent object itself are not rendered."""
        # Both columns are requested explicitly. configure() honours include_columns
        # before the view's override runs, so without the override they would show.
        response = self.client.get(
            reverse("ipam:prefix_aclstandardrules", kwargs={"pk": self.prefix.pk}),
            {"include_columns": "source,source_type"},
        )
        self.assertHttpStatus(response, 200)
        rendered = [column.name for column in response.context["table"].columns]
        self.assertNotIn("source", rendered)
        self.assertNotIn("source_type", rendered)
        self.assertIn("access_list", rendered)

    def test_standard_tab_badge_counts_the_referencing_rules(self):
        """Test that the standard tab badge reports what the tab lists."""
        for _url_name, parent, expected in self.standard_tab_cases():
            with self.subTest(parent=parent):
                rendered = ACLStandardRuleChildrenView.tab.render(parent)
                self.assertIsNotNone(rendered)
                self.assertEqual(rendered["badge"], len(expected))

    def test_standard_tab_is_hidden_when_nothing_references_the_object(self):
        """Test that an unreferenced object shows no standard rule tab at all."""
        self.assertIsNone(ACLStandardRuleChildrenView.tab.render(self.unused_prefix))

    def test_extended_tab_lists_rules_from_either_end(self):
        """Test that each extended rule tab returns its parent's references and nothing else."""
        for url_name, parent, expected in self.extended_tab_cases():
            with self.subTest(view=url_name, parent=parent):
                response = self.client.get(reverse(url_name, kwargs={"pk": parent.pk}))
                self.assertHttpStatus(response, 200)
                self.assertEqual(
                    {row.pk for row in response.context["table"].data},
                    {rule.pk for rule in expected},
                )

    def test_extended_tab_keeps_both_endpoint_columns(self):
        """Test that the extended tab renders the columns carrying the rule's context."""
        response = self.client.get(
            reverse("ipam:prefix_aclextendedrules", kwargs={"pk": self.prefix.pk}),
        )
        self.assertHttpStatus(response, 200)
        rendered = [column.name for column in response.context["table"].columns]
        self.assertIn("source", rendered)
        self.assertIn("destination", rendered)
        self.assertIn("used_as", rendered)

    def test_extended_tab_lists_a_dual_reference_once(self):
        """Test that a rule using the parent at both ends produces a single row."""
        response = self.client.get(
            reverse("ipam:prefix_aclextendedrules", kwargs={"pk": self.prefix.pk}),
        )
        self.assertHttpStatus(response, 200)
        rows = [row.pk for row in response.context["table"].data]
        self.assertEqual(len(rows), len(set(rows)))
        self.assertEqual(rows.count(self.extended_both.pk), 1)

    def test_extended_tab_reports_the_usage_role(self):
        """Test that each row is annotated with the end that references the parent."""
        response = self.client.get(
            reverse("ipam:prefix_aclextendedrules", kwargs={"pk": self.prefix.pk}),
        )
        self.assertHttpStatus(response, 200)
        self.assertEqual(
            {row.pk: row.used_as for row in response.context["table"].data},
            {
                self.extended_sources[self.prefix].pk: ACLRuleUsageChoices.USAGE_SOURCE,
                self.extended_destination.pk: ACLRuleUsageChoices.USAGE_DESTINATION,
                self.extended_both.pk: ACLRuleUsageChoices.USAGE_BOTH,
            },
        )

    def test_extended_tab_badge_counts_a_dual_reference_once(self):
        """Test that the extended tab badge reports what the tab lists."""
        for _url_name, parent, expected in self.extended_tab_cases():
            with self.subTest(parent=parent):
                rendered = ACLExtendedRuleChildrenView.tab.render(parent)
                self.assertIsNotNone(rendered)
                self.assertEqual(rendered["badge"], len(expected))

    def test_extended_tab_is_hidden_when_nothing_references_the_object(self):
        """Test that an unreferenced object shows no extended rule tab at all."""
        self.assertIsNone(ACLExtendedRuleChildrenView.tab.render(self.unused_prefix))

    def test_rule_reference_filter_pins_the_content_type(self):
        """Test that the filter constrains the generic FK's type as well as its id."""
        query = rule_reference_filter(self.prefix, "source")
        self.assertIn(("source_type", ContentType.objects.get_for_model(Prefix)), query.children)
        self.assertIn(("source_id", self.prefix.pk), query.children)

    def test_rule_reference_filter_rejects_a_missing_role(self):
        """Test that a role-less call raises rather than matching every rule."""
        with self.assertRaises(ValueError):
            rule_reference_filter(self.prefix)

    def test_both_tabs_are_offered_on_the_parent_page(self):
        """Test that the tabs render on the object page under their own permission."""
        response = self.client.get(reverse("ipam:prefix", kwargs={"pk": self.prefix.pk}))
        self.assertHttpStatus(response, 200)
        self.assertContains(response, reverse("ipam:prefix_aclstandardrules", kwargs={"pk": self.prefix.pk}))
        self.assertContains(response, reverse("ipam:prefix_aclextendedrules", kwargs={"pk": self.prefix.pk}))


class ACLStandardRuleTabPermissionTestCase(ACLRuleTabFixtureMixin, TestCase):
    """A user permitted extended rules only sees no standard rule rows."""

    user_permissions = (
        "netbox_acls.view_accesslist",
        "netbox_acls.view_aclextendedrule",
        "ipam.view_prefix",
    )

    def test_standard_tab_lists_nothing_without_permission(self):
        """Test that the standard tab renders empty for a user who cannot view the rules."""
        response = self.client.get(
            reverse("ipam:prefix_aclstandardrules", kwargs={"pk": self.prefix.pk}),
        )
        self.assertHttpStatus(response, 200)
        self.assertEqual(list(response.context["table"].data), [])

    def test_extended_tab_still_lists_its_rules(self):
        """Test that withholding the standard permission does not affect extended rules."""
        response = self.client.get(
            reverse("ipam:prefix_aclextendedrules", kwargs={"pk": self.prefix.pk}),
        )
        self.assertHttpStatus(response, 200)
        self.assertEqual(
            {row.pk for row in response.context["table"].data},
            {
                self.extended_sources[self.prefix].pk,
                self.extended_destination.pk,
                self.extended_both.pk,
            },
        )


class ACLRuleTabPermissionTestCase(ACLRuleTabFixtureMixin, TestCase):
    """A user permitted one rule type sees that tab's rows and none of the other's."""

    user_permissions = (
        "netbox_acls.view_accesslist",
        "netbox_acls.view_aclstandardrule",
        "ipam.view_prefix",
    )

    def test_standard_tab_still_lists_its_rules(self):
        """Test that withholding the extended permission does not affect standard rules."""
        response = self.client.get(
            reverse("ipam:prefix_aclstandardrules", kwargs={"pk": self.prefix.pk}),
        )
        self.assertHttpStatus(response, 200)
        self.assertEqual(
            {row.pk for row in response.context["table"].data},
            {self.standard_rules[self.prefix].pk, self.standard_second_prefix_rule.pk},
        )

    def test_extended_tab_lists_nothing_without_permission(self):
        """Test that the extended tab renders empty for a user who cannot view the rules."""
        response = self.client.get(
            reverse("ipam:prefix_aclextendedrules", kwargs={"pk": self.prefix.pk}),
        )
        self.assertHttpStatus(response, 200)
        self.assertEqual(list(response.context["table"].data), [])
