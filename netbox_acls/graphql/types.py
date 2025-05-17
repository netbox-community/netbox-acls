"""
Define the object types and queries available via the graphql api.
"""

from typing import Annotated, List, Union

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from .. import models
from . import filters


@strawberry_django.type(
    models.AccessList,
    fields="__all__",
    exclude=["assigned_object_type", "assigned_object_id"],
    filters=filters.AccessListFilter,
)
class AccessListType(NetBoxObjectType):
    """
    Defines the object type for the django model AccessList.
    """

    # Model fields
    assigned_object_type: Annotated["ContentTypeType", strawberry.lazy("netbox.graphql.types")]
    assigned_object: Annotated[
        Union[
            Annotated["DeviceType", strawberry.lazy("dcim.graphql.types")],
            Annotated["VirtualMachineType", strawberry.lazy("virtualization.graphql.types")],
        ],
        strawberry.union("ACLAssignmentType"),
    ]

    # Related models
    aclstandardrules: List[
        Annotated[
            "ACLStandardRuleType",
            strawberry.lazy("netbox_acls.graphql.types"),
        ]
    ]
    aclextendedrules: List[
        Annotated[
            "ACLExtendedRuleType",
            strawberry.lazy("netbox_acls.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACLInterfaceAssignment,
    fields="__all__",
    exclude=["assigned_object_type", "assigned_object_id"],
    filters=filters.ACLInterfaceAssignmentFilter,
)
class ACLInterfaceAssignmentType(NetBoxObjectType):
    """
    Defines the object type for the django model ACLInterfaceAssignment.
    """

    # Model fields
    access_list: Annotated["AccessListType", strawberry.lazy("netbox_acls.graphql.types")]
    assigned_object_type: Annotated["ContentTypeType", strawberry.lazy("netbox.graphql.types")]
    assigned_object: Annotated[
        Union[
            Annotated["InterfaceType", strawberry.lazy("dcim.graphql.types")],
            Annotated["VMInterfaceType", strawberry.lazy("virtualization.graphql.types")],
        ],
        strawberry.union("ACLInterfaceAssignedObjectType"),
    ]


@strawberry_django.type(
    models.ACLStandardRule,
    fields="__all__",
    filters=filters.ACLStandardRuleFilter,
)
class ACLStandardRuleType(NetBoxObjectType):
    """
    Defines the object type for the django model ACLStandardRule.
    """

    # Model fields
    access_list: Annotated["AccessListType", strawberry.lazy("netbox_acls.graphql.types")]
    source_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None


@strawberry_django.type(
    models.ACLExtendedRule,
    fields="__all__",
    filters=filters.ACLExtendedRuleFilter,
)
class ACLExtendedRuleType(NetBoxObjectType):
    """
    Defines the object type for the django model ACLExtendedRule.
    """

    # Model fields
    access_list: Annotated["AccessListType", strawberry.lazy("netbox_acls.graphql.types")]
    source_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None
    source_ports: List[int] | None
    destination_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None
    destination_ports: List[int] | None
