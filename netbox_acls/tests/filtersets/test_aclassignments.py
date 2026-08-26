from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.choices import InterfaceTypeChoices
from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    Manufacturer,
    Region,
    Site,
    SiteGroup,
    VirtualChassis,
)
from ipam.models import Prefix
from utilities.testing import ChangeLoggedFilterSetTestMixin
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ...filtersets import ACLAssignmentFilterSet
from ...models import AccessList, ACLAssignment


class ACLAssignmentFilterSetTestCase(TestCase, ChangeLoggedFilterSetTestMixin):
    """FilterSet tests for ACLAssignment."""

    queryset = ACLAssignment.objects.all()
    filterset = ACLAssignmentFilterSet
    ignore_fields = ("assigned_object_id",)

    @classmethod
    def setUpTestData(cls):
        cls.grandparent_region = Region.objects.create(name="Region 00", slug="region-00")
        cls.parent_region = Region.objects.create(
            name="Region 0",
            slug="region-0",
            parent=cls.grandparent_region,
        )
        cls.region = Region.objects.create(name="Region 1", slug="region-1", parent=cls.parent_region)
        cls.site_group = SiteGroup.objects.create(name="Site Group 1", slug="site-group-1")
        cls.site = Site.objects.create(
            name="Site 1",
            slug="site-1",
            region=cls.region,
            group=cls.site_group,
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Device Type 1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")
        cls.device = Device.objects.create(
            name="Device 1",
            site=cls.site,
            device_type=device_type,
            role=device_role,
        )
        cls.interface1 = cls.device.interfaces.create(
            name="DeviceInterface1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.interface2 = cls.device.interfaces.create(
            name="DeviceInterface2",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        # The chassis master and the VM site exist so the scope filters can be proven
        # through all five assignable target types, not just the two device-backed ones.
        cls.virtual_chassis = VirtualChassis.objects.create(name="Virtual Chassis 1", master=cls.device)

        cluster_type = ClusterType.objects.create(name="Cluster Type 1", slug="cluster-type-1")
        cluster = Cluster.objects.create(name="Cluster 1", type=cluster_type)
        cls.virtual_machine = VirtualMachine.objects.create(name="VM 1", cluster=cluster, site=cls.site)
        cls.vminterface1 = cls.virtual_machine.interfaces.create(name="eth0")

        cls.acl1 = AccessList.objects.create(
            name="testacl1",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        cls.acl2 = AccessList.objects.create(
            name="testacl2",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV6,
            default_action=ACLActionChoices.ACTION_PERMIT,
        )

        # The device/interface/virtual_machine/vminterface filters traverse the reverse
        # GenericRelation query names contributed in models/access_lists.py, so each
        # assignable type needs its own assignment to be reachable. Host assignments
        # carry direction=none, interface assignments carry ingress or egress.
        # family is denormalized from the access list in save(), which bulk_create skips.
        assignments = (
            ACLAssignment(
                access_list=cls.acl1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
                assigned_object_type=ContentType.objects.get_for_model(Interface),
                assigned_object_id=cls.interface1.pk,
                family=cls.acl1.family,
                comments="reviewed quarterly",
            ),
            ACLAssignment(
                access_list=cls.acl1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
                assigned_object_type=ContentType.objects.get_for_model(Interface),
                assigned_object_id=cls.interface2.pk,
                family=cls.acl1.family,
            ),
            ACLAssignment(
                access_list=cls.acl2,
                direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
                assigned_object_type=ContentType.objects.get_for_model(VMInterface),
                assigned_object_id=cls.vminterface1.pk,
                family=cls.acl2.family,
            ),
            ACLAssignment(
                access_list=cls.acl1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
                assigned_object_type=ContentType.objects.get_for_model(Device),
                assigned_object_id=cls.device.pk,
                family=cls.acl1.family,
            ),
            ACLAssignment(
                access_list=cls.acl1,
                direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
                assigned_object_type=ContentType.objects.get_for_model(VirtualChassis),
                assigned_object_id=cls.virtual_chassis.pk,
                family=cls.acl1.family,
            ),
            ACLAssignment(
                access_list=cls.acl2,
                direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
                assigned_object_type=ContentType.objects.get_for_model(VirtualMachine),
                assigned_object_id=cls.virtual_machine.pk,
                family=cls.acl2.family,
            ),
        )
        ACLAssignment.objects.bulk_create(assignments)

    def test_q(self):
        params = {"q": "testacl2"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_q_matches_interface_name(self):
        params = {"q": "DeviceInterface1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_matches_comments(self):
        params = {"q": "reviewed"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_ignores_choice_values(self):
        """Zero is correct here. The direction has its own filter."""
        params = {"q": ACLAssignmentDirectionChoices.DIRECTION_EGRESS}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_q_ignores_blank_terms(self):
        """Ignoring a blank term means returning everything, not nothing."""
        self.assertEqual(self.filterset({"q": "   "}, self.queryset).qs.count(), 6)

    def test_access_list(self):
        params = {"access_list_id": [self.acl1.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"access_list": [self.acl2.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_assigned_object_type(self):
        params = {"assigned_object_type": ["dcim.interface"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"assigned_object_type": ["dcim.interface", "virtualization.vminterface"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {
            "assigned_object_type": [
                "dcim.device",
                "dcim.virtualchassis",
                "virtualization.virtualmachine",
            ],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_assigned_object_type_id(self):
        params = {"assigned_object_type_id": [ContentType.objects.get_for_model(Interface).pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "assigned_object_type_id": [
                ContentType.objects.get_for_model(Device).pk,
                ContentType.objects.get_for_model(VirtualMachine).pk,
            ],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_assigned_object_type_outside_whitelist_matches_nothing(self):
        """limit_choices_to keeps unassignable types off the model, so none can ever match."""
        filterset = self.filterset({"assigned_object_type": ["ipam.prefix"]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 0)

    def test_assigned_object_type_id_outside_whitelist_matches_nothing(self):
        """The pk filter is unrestricted, so an unassignable type matches nothing rather than erroring."""
        params = {"assigned_object_type_id": [ContentType.objects.get_for_model(Prefix).pk]}
        filterset = self.filterset(params, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 0)

    def test_assigned_object_type_drops_unparseable_values(self):
        """A key that is not <app_label>.<model> is skipped, and the remaining keys still filter."""
        for params, expected in (
            ({"assigned_object_type": ["dcim"]}, 0),
            ({"assigned_object_type": ["dcim.interface", "dcim"]}, 2),
        ):
            with self.subTest(params=params):
                filterset = self.filterset(params, self.queryset)
                self.assertEqual(filterset.errors, {})
                self.assertEqual(filterset.qs.count(), expected)

    def test_interface(self):
        params = {"interface_id": [self.interface1.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"interface": [self.interface1.name, self.interface2.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vminterface(self):
        params = {"vminterface_id": [self.vminterface1.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"vminterface": [self.vminterface1.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device(self):
        params = {"device_id": [self.device.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"device": [self.device.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_virtual_machine(self):
        params = {"virtual_machine_id": [self.virtual_machine.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"virtual_machine": [self.virtual_machine.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_virtual_chassis(self):
        params = {"virtual_chassis_id": [self.virtual_chassis.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"virtual_chassis": [self.virtual_chassis.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    # Every assignment resolves to Site 1 by a different relation, so each scope filter matches all 6.
    # A rejected value leaves the count at 6 too, so the errors assertions are what make these bite.

    def test_site(self):
        filterset = self.filterset({"site": [self.site.slug]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 6)

        filterset = self.filterset({"site_id": [self.site.pk]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 6)

    def test_region(self):
        filterset = self.filterset({"region": [self.region.slug]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 6)

        filterset = self.filterset({"region_id": [self.region.pk]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 6)

    def test_site_group(self):
        filterset = self.filterset({"site_group": [self.site_group.slug]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 6)

        filterset = self.filterset({"site_group_id": [self.site_group.pk]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 6)

    def test_region_matches_descendants(self):
        """Selecting an ancestor region matches assignments sited anywhere below it."""
        for region in (self.parent_region, self.grandparent_region):
            with self.subTest(region=region.slug):
                filterset = self.filterset({"region": [region.slug]}, self.queryset)
                self.assertEqual(filterset.errors, {})
                self.assertEqual(filterset.qs.count(), 6)

                filterset = self.filterset({"region_id": [region.pk]}, self.queryset)
                self.assertEqual(filterset.errors, {})
                self.assertEqual(filterset.qs.count(), 6)

    def test_region_excludes_a_sibling_subtree(self):
        """Test an ancestor match stops at its own subtree instead of matching everything.

        The shared fixture sites every assignment under one region, so a filter
        returning the whole table also counts six. This builds one assignment
        outside that tree so over-matching becomes visible.
        """
        outside_region = Region.objects.create(name="Region 9", slug="region-9")
        outside_site = Site.objects.create(name="Site 9", slug="site-9", region=outside_region)
        outside_device = Device.objects.create(
            name="Device 9",
            site=outside_site,
            device_type=self.device.device_type,
            role=self.device.role,
        )
        outside_assignment = ACLAssignment.objects.create(
            access_list=self.acl1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
            assigned_object=outside_device,
        )
        self.assertEqual(self.queryset.count(), 7)

        # The slug and the id take different branches of _filter_nested_scope.
        for region in (self.region, self.parent_region, self.grandparent_region):
            for name, value in (("region", region.slug), ("region_id", region.pk)):
                with self.subTest(region=region.slug, filter=name):
                    filterset = self.filterset({name: [value]}, self.queryset)
                    self.assertEqual(filterset.errors, {})
                    self.assertNotIn(outside_assignment, filterset.qs)
                    self.assertEqual(filterset.qs.count(), 6)

        for name, value in (("region", outside_region.slug), ("region_id", outside_region.pk)):
            with self.subTest(filter=name):
                filterset = self.filterset({name: [value]}, self.queryset)
                self.assertEqual(filterset.errors, {})
                self.assertEqual(list(filterset.qs), [outside_assignment])

    def test_site_group_matches_descendants_and_excludes_a_sibling(self):
        """Test a site group ancestor matches its own subtree and nothing outside it."""
        parent_group = SiteGroup.objects.create(name="Site Group 0", slug="site-group-0")
        self.site_group.parent = parent_group
        self.site_group.save()

        outside_group = SiteGroup.objects.create(name="Site Group 9", slug="site-group-9")
        outside_site = Site.objects.create(name="Site 9", slug="site-9", group=outside_group)
        outside_device = Device.objects.create(
            name="Device 9",
            site=outside_site,
            device_type=self.device.device_type,
            role=self.device.role,
        )
        outside_assignment = ACLAssignment.objects.create(
            access_list=self.acl1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_NONE,
            assigned_object=outside_device,
        )
        self.assertEqual(self.queryset.count(), 7)

        for group in (self.site_group, parent_group):
            for name, value in (("site_group", group.slug), ("site_group_id", group.pk)):
                with self.subTest(group=group.slug, filter=name):
                    filterset = self.filterset({name: [value]}, self.queryset)
                    self.assertEqual(filterset.errors, {})
                    self.assertNotIn(outside_assignment, filterset.qs)
                    self.assertEqual(filterset.qs.count(), 6)

    # Deprecated: the bare names took a primary key from 2.0.0 to 2.0.2, so both forms resolve.

    def test_scope_filters_accept_legacy_primary_keys(self):
        for params in (
            {"site": [str(self.site.pk)]},
            {"region": [str(self.region.pk)]},
            {"site_group": [str(self.site_group.pk)]},
        ):
            with self.subTest(params=params):
                filterset = self.filterset(params, self.queryset)
                self.assertEqual(filterset.errors, {})
                self.assertEqual(filterset.qs.count(), 6)

    def test_scope_filters_prefer_a_slug_over_a_primary_key(self):
        """A numeric slug wins over the site whose primary key it collides with."""
        Site.objects.create(name="Site 2", slug=str(self.site.pk))

        filterset = self.filterset({"site": [str(self.site.pk)]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 0)

    def test_scope_filters_survive_an_out_of_range_number(self):
        """A value too large for the primary key column matches nothing rather than erroring."""
        filterset = self.filterset({"site": ["9" * 40]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 0)

    def test_scope_filters_survive_unparsable_numeric_strings(self):
        """str.isdigit() accepts a superscript, and int() rejects it and over-long strings."""
        for value in ("²", "9" * 5000):
            with self.subTest(value=value):
                filterset = self.filterset({"site": [value]}, self.queryset)
                self.assertEqual(filterset.errors, {})
                self.assertEqual(filterset.qs.count(), 0)

    def test_scope_filters_ignore_absent_parameters(self):
        """An absent scope parameter filters nothing out."""
        self.assertEqual(self.filterset({}, self.queryset).qs.count(), 6)

    def test_scope_filters_reject_unresolvable_values(self):
        """A value that resolves to no object matches nothing, not everything."""
        # The absent ID has to be truthy, since the multi-value field discards falsy entries.
        absent = 999999
        for params in (
            {"site": ["no-such-site"]},
            {"site_id": [absent]},
            {"region": ["no-such-region"]},
            {"region_id": [absent]},
            {"site_group": ["no-such-group"]},
            {"site_group_id": [absent]},
        ):
            with self.subTest(params=params):
                self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    # direction and family are single-valued ChoiceFilters, so assert one value at a time.

    def test_direction(self):
        params = {"direction": ACLAssignmentDirectionChoices.DIRECTION_EGRESS}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"direction": ACLAssignmentDirectionChoices.DIRECTION_INGRESS}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_family(self):
        params = {"family": ACLFamilyChoices.FAMILY_IPV4}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"family": ACLFamilyChoices.FAMILY_IPV6}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
