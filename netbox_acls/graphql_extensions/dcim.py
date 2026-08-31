"""ACL additions to NetBox's DCIM GraphQL types."""

import strawberry

from .base import ACLAssignmentReferences

__all__ = (
    "DeviceTypeExtension",
    "InterfaceTypeExtension",
    "VirtualChassisTypeExtension",
)


@strawberry.type
class DeviceTypeExtension(ACLAssignmentReferences):
    """ACL additions to NetBox's Device type."""

    models = ["dcim.device"]


@strawberry.type
class InterfaceTypeExtension(ACLAssignmentReferences):
    """ACL additions to NetBox's Interface type."""

    models = ["dcim.interface"]


@strawberry.type
class VirtualChassisTypeExtension(ACLAssignmentReferences):
    """ACL additions to NetBox's VirtualChassis type."""

    models = ["dcim.virtualchassis"]
