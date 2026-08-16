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
from utilities.testing import ChangeLoggedFilterSetTests
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ...filtersets import ACLAssignmentFilterSet
from ...models import AccessList, ACLAssignment


class ACLAssignmentFilterSetTestCase(TestCase, ChangeLoggedFilterSetTests):
    """FilterSet tests for ACLAssignment."""

    queryset = ACLAssignment.objects.all()
    filterset = ACLAssignmentFilterSet
    ignore_fields = ("assigned_object_id",)

    @classmethod
    def setUpTestData(cls):
        cls.parent_region = Region.objects.create(name="Region 0", slug="region-0")
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
        """Selecting a parent region matches assignments sited in its children."""
        filterset = self.filterset({"region": [self.parent_region.slug]}, self.queryset)
        self.assertEqual(filterset.errors, {})
        self.assertEqual(filterset.qs.count(), 6)

        filterset = self.filterset({"region_id": [self.parent_region.pk]}, self.queryset)
        self.assertEqual(filterset.errors, {})
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
