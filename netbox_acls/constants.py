"""
Constants for filters
"""

from django.db.models import Q

#
# AccessList
#

ACL_HOST_ASSIGNMENT_MODELS = Q(
    Q(app_label="dcim", model="device")
    | Q(app_label="dcim", model="virtualchassis")
    | Q(app_label="virtualization", model="virtualmachine"),
)

#
# ACLInterfaceAssignment
#

ACL_INTERFACE_ASSIGNMENT_MODELS = Q(
    Q(app_label="dcim", model="interface") | Q(app_label="virtualization", model="vminterface"),
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
