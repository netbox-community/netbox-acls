"""
Defines the various choices to be used by the models, forms, and other plugin specifics.
"""

from utilities.choices import ChoiceSet

__all__ = (
    "ACLActionChoices",
    "ACLAssignmentDirectionChoices",
    "ACLAssignmentDirectionUIChoices",
    "ACLFamilyChoices",
    "ACLProtocolChoices",
    "ACLRuleActionChoices",
    "ACLRuleLogOptionChoices",
    "ACLRuleUsageChoices",
    "ACLTypeChoices",
)


class ACLActionChoices(ChoiceSet):
    """
    Defines the choices available for the Access Lists plugin specific to ACL default_action.
    """

    ACTION_DENY = "deny"
    ACTION_PERMIT = "permit"
    ACTION_REJECT = "reject"

    CHOICES = [
        (ACTION_DENY, "Deny", "red"),
        (ACTION_PERMIT, "Permit", "green"),
        (ACTION_REJECT, "Reject (Reset)", "orange"),
    ]


class ACLFamilyChoices(ChoiceSet):
    """
    Defines the IP protocol families available for the Access Lists.
    """

    key = "netbox_acls.AccessList.family"

    FAMILY_DUAL = "dual"
    FAMILY_IPV4 = "ipv4"
    FAMILY_IPV6 = "ipv6"

    CHOICES = [
        (FAMILY_IPV4, "IPv4", "blue"),
        (FAMILY_IPV6, "IPv6", "purple"),
        (FAMILY_DUAL, "Dual", "cyan"),
    ]


class ACLRuleActionChoices(ChoiceSet):
    """
    Defines the choices available for the Access Lists plugin specific to ACL rule actions.
    """

    ACTION_DENY = "deny"
    ACTION_PERMIT = "permit"
    ACTION_REMARK = "remark"

    CHOICES = [
        (ACTION_DENY, "Deny", "red"),
        (ACTION_PERMIT, "Permit", "green"),
        (ACTION_REMARK, "Remark", "blue"),
    ]


class ACLRuleLogOptionChoices(ChoiceSet):
    """
    Logging options available to ACL rules.
    """

    key = "ACLRule.log_options"

    OPTION_SYSLOG = "syslog"
    OPTION_CISCO_LOG_INPUT = "cisco-log-input"

    CHOICES = [
        (
            "Generic",
            ((OPTION_SYSLOG, "Syslog", "blue"),),
        ),
        (
            "Cisco",
            ((OPTION_CISCO_LOG_INPUT, "Log-input", "purple"),),
        ),
    ]


class ACLRuleUsageChoices(ChoiceSet):
    """
    Defines how an ACL Extended Rule references an object listed against it.
    """

    USAGE_SOURCE = "source"
    USAGE_DESTINATION = "destination"
    USAGE_BOTH = "both"

    CHOICES = [
        (USAGE_SOURCE, "Source", "blue"),
        (USAGE_DESTINATION, "Destination", "purple"),
        (USAGE_BOTH, "Source and destination", "teal"),
    ]


class ACLAssignmentDirectionUIChoices(ChoiceSet):
    """
    Defines the application direction of the ACL on an associated interface (UI version).
    """

    DIRECTION_INGRESS = "ingress"
    DIRECTION_EGRESS = "egress"

    CHOICES = [
        (DIRECTION_INGRESS, "Ingress", "blue"),
        (DIRECTION_EGRESS, "Egress", "purple"),
    ]


class ACLAssignmentDirectionChoices(ChoiceSet):
    """
    Defines the application direction of the ACL on an associated interface.
    """

    DIRECTION_INGRESS = "ingress"
    DIRECTION_EGRESS = "egress"
    DIRECTION_NONE = "none"

    CHOICES = [
        (DIRECTION_INGRESS, "Ingress", "blue"),
        (DIRECTION_EGRESS, "Egress", "purple"),
        (DIRECTION_NONE, "N/A", "darkgray"),
    ]


class ACLTypeChoices(ChoiceSet):
    """
    Defines the choices available for the Access Lists plugin specific to ACL type.
    """

    TYPE_STANDARD = "standard"
    TYPE_EXTENDED = "extended"

    CHOICES = [
        (TYPE_EXTENDED, "Extended", "purple"),
        (TYPE_STANDARD, "Standard", "blue"),
    ]


class ACLProtocolChoices(ChoiceSet):
    """
    Defines the choices available for the Access Lists plugin specific to ACL Rule protocol.
    """

    key = "ACLExtendedRule.protocol"

    PROTOCOL_EIGRP = "eigrp"
    PROTOCOL_GRE = "gre"
    PROTOCOL_ICMP = "icmp"
    PROTOCOL_IP = "ip"
    PROTOCOL_OSPF = "ospf"
    PROTOCOL_PIM = "pim"
    PROTOCOL_TCP = "tcp"
    PROTOCOL_UDP = "udp"

    # The second group follows the IP protocol numbers 47, 88, 89 and 103.
    CHOICES = [
        (
            "Common",
            (
                (PROTOCOL_ICMP, "ICMP", "purple"),
                (PROTOCOL_IP, "IP", "cyan"),
                (PROTOCOL_TCP, "TCP", "blue"),
                (PROTOCOL_UDP, "UDP", "orange"),
            ),
        ),
        (
            "Routing and tunneling",
            (
                (PROTOCOL_GRE, "GRE", "teal"),
                (PROTOCOL_EIGRP, "EIGRP", "yellow"),
                (PROTOCOL_OSPF, "OSPF", "green"),
                (PROTOCOL_PIM, "PIM", "indigo"),
            ),
        ),
    ]
