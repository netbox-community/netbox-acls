"""ACL additions to NetBox's virtualization GraphQL types."""

import strawberry

from .base import ACLAssignmentReferences

__all__ = (
    "VMInterfaceTypeExtension",
    "VirtualMachineTypeExtension",
)


@strawberry.type
class VirtualMachineTypeExtension(ACLAssignmentReferences):
    """ACL additions to NetBox's VirtualMachine type."""

    models = ["virtualization.virtualmachine"]


@strawberry.type
class VMInterfaceTypeExtension(ACLAssignmentReferences):
    """ACL additions to NetBox's VMInterface type."""

    models = ["virtualization.vminterface"]
