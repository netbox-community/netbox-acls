from django.contrib.contenttypes.models import ContentType

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from utilities.testing import ViewTestCases, create_tags
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from ...choices import (
    ACLActionChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLAssignment
from .base import PluginTestCases


class ACLAssignmentViewTestCase(
    PluginTestCases.ObjectViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
):
    """View tests for ACLAssignment."""

    model = ACLAssignment
    user_permissions = (
        "dcim.view_site",
        "dcim.view_devicetype",
        "dcim.view_device",
        "dcim.view_interface",
        "virtualization.view_cluster",
        "virtualization.view_clustergroup",
        "virtualization.view_clustertype",
        "virtualization.view_virtualmachine",
        "virtualization.view_vminterface",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Device Type 1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")
        cls.device = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=device_type,
            role=device_role,
        )
        interface1 = cls.device.interfaces.create(
            name="DeviceInterface1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        interface2 = cls.device.interfaces.create(
            name="DeviceInterface2",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.interface3 = cls.device.interfaces.create(
            name="DeviceInterface3",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        cluster_type = ClusterType.objects.create(name="Cluster Type 1", slug="cluster-type-1")
        cluster = Cluster.objects.create(name="Cluster 1", type=cluster_type)
        cls.virtual_machine = VirtualMachine.objects.create(name="VM 1", cluster=cluster)
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

        # bulk_create skips save(), where family is copied from the access list.
        ACLAssignment.objects.bulk_create(
            (
                ACLAssignment(
                    access_list=cls.acl1,
                    direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
                    assigned_object_type=ContentType.objects.get_for_model(Interface),
                    assigned_object_id=interface1.pk,
                    family=cls.acl1.family,
                ),
                ACLAssignment(
                    access_list=cls.acl1,
                    direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
                    assigned_object_type=ContentType.objects.get_for_model(Interface),
                    assigned_object_id=interface2.pk,
                    family=cls.acl1.family,
                ),
                ACLAssignment(
                    access_list=cls.acl2,
                    direction=ACLAssignmentDirectionChoices.DIRECTION_EGRESS,
                    assigned_object_type=ContentType.objects.get_for_model(VMInterface),
                    assigned_object_id=cls.vminterface1.pk,
                    family=cls.acl2.family,
                ),
            ),
        )
        # bulk_create returns no primary keys.
        cls.assignments = list(ACLAssignment.objects.order_by("pk"))

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # The object picker's queryset comes from the posted type, so both keys
        # have to arrive together.
        cls.form_data = {
            "access_list": cls.acl1.pk,
            "assigned_object_content_type": ContentType.objects.get_for_model(Interface).pk,
            "assigned_object_object_id": cls.interface3.pk,
            "direction": ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
            "comments": "",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "comments": "Bulk edited",
        }

        # No row may repeat an existing target and direction, or an ACL name on a host.
        cls.csv_data = (
            "access_list,assigned_object_type,assigned_object,assigned_object_parent,direction",
            f"{cls.acl1.name},dcim.device,{cls.device.name},,none",
            f"{cls.acl1.name},dcim.interface,{cls.interface3.name},{cls.device.name},ingress",
            f"{cls.acl2.name},virtualization.vminterface,{cls.vminterface1.name},{cls.virtual_machine.name},ingress",
        )

        cls.csv_update_data = (
            "id,comments",
            f"{cls.assignments[0].pk},Updated by import",
            f"{cls.assignments[1].pk},Updated by import too",
        )

    def test_detail_view_renders_the_assignment_attributes(self):
        """Test that the detail view renders the assignment attributes."""
        self.add_permissions("netbox_acls.view_aclassignment")
        # Two interface assignments share this access list, so select on direction.
        assignment = ACLAssignment.objects.get(
            access_list=self.acl1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        response = self.client.get(assignment.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, assignment.access_list.get_absolute_url())
        self.assertContains(response, assignment.assigned_object.get_absolute_url())
        self.assertContains(response, assignment.get_direction_display())

    def test_assignment_links_the_parent_of_its_target(self):
        """Test that an interface assignment renders a link to its parent."""
        self.add_permissions("netbox_acls.view_aclassignment")

        for model_name, parent_field in (
            ("interface", "device"),
            ("vminterface", "virtual_machine"),
        ):
            with self.subTest(assigned_object_type=model_name):
                assignment = ACLAssignment.objects.filter(
                    assigned_object_type__model=model_name,
                ).earliest("pk")
                parent = getattr(assignment.assigned_object, parent_field)

                response = self.client.get(assignment.get_absolute_url())

                self.assertHttpStatus(response, 200)
                self.assertContains(response, assignment.assigned_object.get_absolute_url())
                self.assertContains(response, parent.get_absolute_url())

    def test_detail_view_renders_the_panel_attributes(self):
        """Test that the detail view renders the panel's own attribute anchors."""
        self.add_permissions("netbox_acls.view_aclassignment")
        assignment = ACLAssignment.objects.get(
            access_list=self.acl1,
            direction=ACLAssignmentDirectionChoices.DIRECTION_INGRESS,
        )

        response = self.client.get(assignment.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'id="attr_assigned_object"')
