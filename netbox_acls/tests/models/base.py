from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Manufacturer,
    Site,
    VirtualChassis,
)
from django.test import TestCase
from ipam.models import RIR, Aggregate, IPAddress, IPRange, Prefix
from netaddr import IPNetwork
from virtualization.models import Cluster, ClusterType, VirtualMachine


class BaseTestCase(TestCase):
    """
    Base test case for netbox_acls models.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create base data to test using including
          - 1 of each of the following: rir, site, manufacturer, device type,
            device role, cluster type, cluster, virtual chassis, and
            virtual machine
          - 2 of each device, aggregate, ip address, ip range, prefix, service
        """

        # RIR
        rir = RIR.objects.create(
            name="RIR 1",
            slug="rir-1",
        )

        # Sites
        site = Site.objects.create(
            name="Site 1",
            slug="site-1",
        )

        # Device Types
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer 1",
            slug="manufacturer-1",
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Device Type 1",
        )

        # Device Roles
        device_role = DeviceRole.objects.create(
            name="Device Role 1",
            slug="device-role-1",
        )

        # Devices
        cls.device1 = Device.objects.create(
            name="Device 1",
            site=site,
            device_type=device_type,
            role=device_role,
        )
        cls.device2 = Device.objects.create(
            name="Device 2",
            site=site,
            device_type=device_type,
            role=device_role,
        )

        # Virtual Chassis
        cls.virtual_chassis1 = VirtualChassis.objects.create(
            name="Virtual Chassis 1",
        )

        # Virtual Chassis Members
        cls.virtual_chassis_member1 = Device.objects.create(
            name="VC Device",
            site=site,
            device_type=device_type,
            role=device_role,
            virtual_chassis=cls.virtual_chassis1,
            vc_position=1,
        )

        # Virtualization Cluster Type
        cluster_type = ClusterType.objects.create(
            name="Cluster Type 1",
        )

        # Virtualization Cluster
        cluster = Cluster.objects.create(
            name="Cluster 1",
            type=cluster_type,
        )

        # Virtualization Cluster Member
        cls.cluster_member1 = Device.objects.create(
            name="Cluster Device",
            site=site,
            device_type=device_type,
            role=device_role,
        )

        # Virtual Machine
        cls.virtual_machine1 = VirtualMachine.objects.create(
            name="VirtualMachine 1",
            status="active",
            cluster=cluster,
        )
        cls.virtual_machine2 = VirtualMachine.objects.create(
            name="VirtualMachine 2",
            status="active",
            cluster=cluster,
        )

        # Aggregate
        cls.aggregate1 = Aggregate.objects.create(
            prefix=IPNetwork("10.0.0.0/8"),
            rir=rir,
        )
        cls.aggregate2 = Aggregate.objects.create(
            prefix=IPNetwork("172.16.0.0/12"),
            rir=rir,
        )

        # IP Address
        cls.ip_address1 = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
        )
        cls.ip_address2 = IPAddress.objects.create(
            address=IPNetwork("10.0.0.2/24"),
        )

        # IP Range
        cls.ip_range1 = IPRange.objects.create(
            start_address=IPNetwork("10.0.1.1/24"),
            end_address=IPNetwork("10.0.1.254/24"),
        )
        cls.ip_range2 = IPRange.objects.create(
            start_address=IPNetwork("10.0.2.1/24"),
            end_address=IPNetwork("10.0.2.254/24"),
        )

        # Prefix
        cls.prefix1 = Prefix.objects.create(
            prefix=IPNetwork("10.1.0.0/16"),
        )
        cls.prefix2 = Prefix.objects.create(
            prefix=IPNetwork("10.2.0.0/16"),
        )
