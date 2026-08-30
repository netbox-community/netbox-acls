"""Extensions contributed to NetBox's own GraphQL types.

Kept out of the graphql package, whose __init__ assembles this plugin's types
before these register. No module here may import a core GraphQL module at
import time.
"""

from .dcim import DeviceTypeExtension, InterfaceTypeExtension, VirtualChassisTypeExtension
from .ipam import (
    AggregateTypeExtension,
    IPAddressTypeExtension,
    IPRangeTypeExtension,
    PrefixTypeExtension,
)
from .virtualization import VirtualMachineTypeExtension, VMInterfaceTypeExtension

__all__ = (
    "AggregateTypeExtension",
    "DeviceTypeExtension",
    "IPAddressTypeExtension",
    "IPRangeTypeExtension",
    "InterfaceTypeExtension",
    "PrefixTypeExtension",
    "VMInterfaceTypeExtension",
    "VirtualChassisTypeExtension",
    "VirtualMachineTypeExtension",
    "type_extensions",
)

type_extensions = [
    AggregateTypeExtension,
    DeviceTypeExtension,
    InterfaceTypeExtension,
    IPAddressTypeExtension,
    IPRangeTypeExtension,
    PrefixTypeExtension,
    VirtualChassisTypeExtension,
    VirtualMachineTypeExtension,
    VMInterfaceTypeExtension,
]
