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
