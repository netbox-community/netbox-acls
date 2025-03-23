from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Manufacturer,
    Site,
)
from django.test import TestCase
from ipam.models import Prefix
from virtualization.models import VirtualMachine


class BaseTestCase(TestCase):
    """
    Base test case for netbox_acls models.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create base data to test using including
          - 1 of each of the following: test site, manufacturer, device type
            device role, cluster type, cluster, virtual_chassis, and
            virtual machine
          - 2 devices, prefixes, 2 interfaces, and 2 vminterfaces
        """

        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer 1",
            slug="manufacturer-1",
        )
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Device Type 1",
        )
        devicerole = DeviceRole.objects.create(
            name="Device Role 1",
            slug="device-role-1",
        )
        device = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=devicetype,
            device_role=devicerole,
        )
        # virtual_chassis = VirtualChassis.objects.create(name="Virtual Chassis 1")
        # virtual_chassis_member = Device.objects.create(
        #    name="VC Device",
        #    site=site,
        #    device_type=devicetype,
        #    device_role=devicerole,
        #    virtual_chassis=virtual_chassis,
        #    vc_position=1,
        # )
        # cluster_member = Device.objects.create(
        #    name="Cluster Device",
        #    site=site,
        #    device_type=devicetype,
        #    device_role=devicerole,
        # )
        # clustertype = ClusterType.objects.create(name="Cluster Type 1")
        # cluster = Cluster.objects.create(
        #    name="Cluster 1",
        #    type=clustertype,
        # )
        virtual_machine = VirtualMachine.objects.create(name="VirtualMachine 1")
        virtual_machine.save()
        prefix = Prefix.objects.create(prefix="10.0.0.0/8")
