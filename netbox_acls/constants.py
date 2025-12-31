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

#
# AccessList Rule
#

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
