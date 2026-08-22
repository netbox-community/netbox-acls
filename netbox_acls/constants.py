"""
Constants for filters
"""

from django.db.models import Q

#
# AccessList Assignments
#

ACL_ASSIGNMENT_MODELS = Q(
    Q(
        app_label="dcim",
        model__in=(
            "device",
            "interface",
            "virtualchassis",
        ),
    )
    | Q(
        app_label="virtualization",
        model__in=(
            "virtualmachine",
            "vminterface",
        ),
    )
)

# Natural value per assignable content type, for import. Must match ACL_ASSIGNMENT_MODELS exactly.
ACL_ASSIGNMENT_OBJECT_LOOKUPS = {
    "dcim.device": "name",
    "dcim.interface": "name",
    "dcim.virtualchassis": "name",
    "virtualization.virtualmachine": "name",
    "virtualization.vminterface": "name",
}

# Path from an assignable target to the parent that makes its name unique.
ACL_ASSIGNMENT_OBJECT_PARENT_LOOKUPS = {
    "dcim.interface": "device__name",
    "virtualization.vminterface": "virtual_machine__name",
}

# Query paths from an ACL assignment to the object carrying its site, one per assignable
# target type. Each leading segment is the reverse generic relation query name contributed
# to that model in models/access_lists.py.
ACL_ASSIGNMENT_SITE_TRAVERSAL_PATHS = (
    "device",
    "interface__device",
    "virtual_chassis__master",
    "virtual_machine",
    "vminterface__virtual_machine",
)

#
# AccessList Rule
#

ACL_RULE_PORT_MIN, ACL_RULE_PORT_MAX = 1, 65535


ACL_RULE_SOURCE_DESTINATION_MODELS = Q(
    Q(
        app_label="ipam",
        model__in=(
            "aggregate",
            "ipaddress",
            "iprange",
            "prefix",
        ),
    )
)

# Natural value per source or destination content type, for import. None means ID only.
# Must match ACL_RULE_SOURCE_DESTINATION_MODELS exactly.
ACL_RULE_OBJECT_LOOKUPS = {
    "ipam.aggregate": "prefix",
    "ipam.ipaddress": "address",
    "ipam.iprange": None,
    "ipam.prefix": "prefix",
}
