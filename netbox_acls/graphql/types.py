"""
Define the object types and queries available via the graphql api.
"""

from typing import Annotated, List, Union, TYPE_CHECKING

import strawberry
import strawberry_django
from netbox.graphql.types import ContentTypeType, NetBoxObjectType

from .. import models
from . import filters

if TYPE_CHECKING:
    from dcim.graphql.types import DeviceType, InterfaceType
    from ipam.graphql.types import AggregateType, IPAddressType, IPRangeType, PrefixType
    from virtualization.graphql.types import VirtualMachineType, VMInterfaceType


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
    exclude=[
        "source_id",
        "source_type",
    ],
    filters=filters.ACLStandardRuleFilter,
)
class ACLStandardRuleType(NetBoxObjectType):
    """
    Defines the object type for the django model ACLStandardRule.
    """

    # Model fields
    access_list: Annotated["AccessListType", strawberry.lazy("netbox_acls.graphql.types")]
    source_type: Annotated["ContentTypeType", strawberry.lazy("netbox.graphql.types")] | None
    source: (
        Annotated[
            Union[
                Annotated[
                    "AggregateType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "IPAddressType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "IPRangeType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "PrefixType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
            ],
            strawberry.union("ACLStandardRuleObjectType"),
        ]
        | None
    )

    # Cached related source objects
    _source_aggregate: Annotated["AggregateType", strawberry.lazy("ipam.graphql.types")] | None
    _source_ipaddress: Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")] | None
    _source_iprange: Annotated["IPRangeType", strawberry.lazy("ipam.graphql.types")] | None
    _source_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None


@strawberry_django.type(
    models.ACLExtendedRule,
    fields="__all__",
    exclude=[
        "source_id",
        "source_type",
        "destination_id",
        "destination_type",
    ],
    filters=filters.ACLExtendedRuleFilter,
)
class ACLExtendedRuleType(NetBoxObjectType):
    """
    Defines the object type for the django model ACLExtendedRule.
    """

    # Model fields
    access_list: Annotated["AccessListType", strawberry.lazy("netbox_acls.graphql.types")]
    source_type: Annotated["ContentTypeType", strawberry.lazy("netbox.graphql.types")] | None
    source: (
        Annotated[
            Union[
                Annotated[
                    "AggregateType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "IPAddressType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "IPRangeType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "PrefixType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
            ],
            strawberry.union("ACLStandardRuleObjectType"),
        ]
        | None
    )
    source_ports: List[int] | None
    destination_type: Annotated["ContentTypeType", strawberry.lazy("netbox.graphql.types")] | None
    destination: (
        Annotated[
            Union[
                Annotated[
                    "AggregateType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "IPAddressType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "IPRangeType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
                Annotated[
                    "PrefixType",
                    strawberry.lazy("ipam.graphql.types"),
                ],
            ],
            strawberry.union("ACLStandardRuleObjectType"),
        ]
        | None
    )
    destination_ports: List[int] | None

    # Cached related source objects
    _source_aggregate: Annotated["AggregateType", strawberry.lazy("ipam.graphql.types")] | None
    _source_ipaddress: Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")] | None
    _source_iprange: Annotated["IPRangeType", strawberry.lazy("ipam.graphql.types")] | None
    _source_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None

    # Cached related destination objects
    _destination_aggregate: Annotated["AggregateType", strawberry.lazy("ipam.graphql.types")] | None
    _destination_ipaddress: Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")] | None
    _destination_iprange: Annotated["IPRangeType", strawberry.lazy("ipam.graphql.types")] | None
    _destination_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None
