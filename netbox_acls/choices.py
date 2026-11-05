"""
Defines the various choices to be used by the models, forms, and other plugin specifics.
"""

from utilities.choices import ChoiceSet

__all__ = (
    "ACLActionChoices",
    "ACLAddressFamilyChoices",
    "ACLAssignmentDirectionChoices",
    "ACLAssignmentDirectionUIChoices",
    "ACLFamilyChoices",
    "ACLICMPTypeChoices",
    "ACLICMPv4TypeChoices",
    "ACLICMPv6TypeChoices",
    "ACLProtocolChoices",
    "ACLRuleActionChoices",
    "ACLRuleLogOptionChoices",
    "ACLRuleUsageChoices",
    "ACLTCPFlagChoices",
    "ACLTCPFlagMatchChoices",
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


class ACLAddressFamilyChoices(ChoiceSet):
    """
    Single IP families supported by address groups.
    """

    key = "ACLAddressGroup.family"

    FAMILY_IPV4 = "ipv4"
    FAMILY_IPV6 = "ipv6"

    CHOICES = [
        (FAMILY_IPV4, "IPv4", "blue"),
        (FAMILY_IPV6, "IPv6", "purple"),
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
    PROTOCOL_ICMPV4 = "icmpv4"
    PROTOCOL_ICMPV6 = "icmpv6"
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
                (PROTOCOL_ICMPV4, "ICMPv4", "purple"),
                (PROTOCOL_ICMPV6, "ICMPv6", "purple"),
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


class ACLICMPv4TypeChoices(ChoiceSet):
    """
    Common ICMPv4 message types offered as numeric presets.
    """

    TYPE_ECHO_REPLY = 0
    TYPE_DESTINATION_UNREACHABLE = 3
    TYPE_REDIRECT = 5
    TYPE_ECHO_REQUEST = 8
    TYPE_ROUTER_ADVERTISEMENT = 9
    TYPE_ROUTER_SOLICITATION = 10
    TYPE_TIME_EXCEEDED = 11
    TYPE_PARAMETER_PROBLEM = 12
    TYPE_TIMESTAMP = 13
    TYPE_TIMESTAMP_REPLY = 14

    CHOICES = [
        (TYPE_ECHO_REPLY, "Echo reply (0)"),
        (TYPE_DESTINATION_UNREACHABLE, "Destination unreachable (3)"),
        (TYPE_REDIRECT, "Redirect (5)"),
        (TYPE_ECHO_REQUEST, "Echo request (8)"),
        (TYPE_ROUTER_ADVERTISEMENT, "Router advertisement (9)"),
        (TYPE_ROUTER_SOLICITATION, "Router solicitation (10)"),
        (TYPE_TIME_EXCEEDED, "Time exceeded (11)"),
        (TYPE_PARAMETER_PROBLEM, "Parameter problem (12)"),
        (TYPE_TIMESTAMP, "Timestamp (13)"),
        (TYPE_TIMESTAMP_REPLY, "Timestamp reply (14)"),
    ]


class ACLICMPv6TypeChoices(ChoiceSet):
    """
    Common ICMPv6 message types offered as numeric presets.
    """

    TYPE_DESTINATION_UNREACHABLE = 1
    TYPE_PACKET_TOO_BIG = 2
    TYPE_TIME_EXCEEDED = 3
    TYPE_PARAMETER_PROBLEM = 4
    TYPE_ECHO_REQUEST = 128
    TYPE_ECHO_REPLY = 129
    TYPE_MULTICAST_LISTENER_QUERY = 130
    TYPE_MULTICAST_LISTENER_REPORT = 131
    TYPE_MULTICAST_LISTENER_DONE = 132
    TYPE_ROUTER_SOLICITATION = 133
    TYPE_ROUTER_ADVERTISEMENT = 134
    TYPE_NEIGHBOR_SOLICITATION = 135
    TYPE_NEIGHBOR_ADVERTISEMENT = 136
    TYPE_REDIRECT = 137
    TYPE_MULTICAST_LISTENER_REPORT_V2 = 143

    CHOICES = [
        (TYPE_DESTINATION_UNREACHABLE, "Destination unreachable (1)"),
        (TYPE_PACKET_TOO_BIG, "Packet too big (2)"),
        (TYPE_TIME_EXCEEDED, "Time exceeded (3)"),
        (TYPE_PARAMETER_PROBLEM, "Parameter problem (4)"),
        (TYPE_ECHO_REQUEST, "Echo request (128)"),
        (TYPE_ECHO_REPLY, "Echo reply (129)"),
        (TYPE_MULTICAST_LISTENER_QUERY, "Multicast listener query (130)"),
        (TYPE_MULTICAST_LISTENER_REPORT, "Multicast listener report (131)"),
        (TYPE_MULTICAST_LISTENER_DONE, "Multicast listener done (132)"),
        (TYPE_ROUTER_SOLICITATION, "Router solicitation (133)"),
        (TYPE_ROUTER_ADVERTISEMENT, "Router advertisement (134)"),
        (TYPE_NEIGHBOR_SOLICITATION, "Neighbor solicitation (135)"),
        (TYPE_NEIGHBOR_ADVERTISEMENT, "Neighbor advertisement (136)"),
        (TYPE_REDIRECT, "Redirect (137)"),
        (TYPE_MULTICAST_LISTENER_REPORT_V2, "Multicast listener report v2 (143)"),
    ]


class ACLICMPTypeChoices(ChoiceSet):
    """
    ICMPv4 and ICMPv6 type presets in one list, labelled with their family.
    """

    # Flat, since the preset widget renders no option groups.
    CHOICES = [
        *((value, f"ICMPv4: {label}") for value, label in ACLICMPv4TypeChoices.CHOICES),
        *((value, f"ICMPv6: {label}") for value, label in ACLICMPv6TypeChoices.CHOICES),
    ]


class ACLTCPFlagChoices(ChoiceSet):
    """
    TCP header flags available to ACL extended rules.
    """

    FLAG_ACK = "ack"
    FLAG_AE = "ae"
    FLAG_CWR = "cwr"
    FLAG_ECE = "ece"
    FLAG_FIN = "fin"
    FLAG_PSH = "psh"
    FLAG_RST = "rst"
    FLAG_SYN = "syn"
    FLAG_URG = "urg"

    # Ordered by header bit, least significant first.
    CHOICES = [
        (FLAG_FIN, "FIN", "orange"),
        (FLAG_SYN, "SYN", "green"),
        (FLAG_RST, "RST", "red"),
        (FLAG_PSH, "PSH", "cyan"),
        (FLAG_ACK, "ACK", "blue"),
        (FLAG_URG, "URG", "yellow"),
        (FLAG_ECE, "ECE", "teal"),
        (FLAG_CWR, "CWR", "indigo"),
        (FLAG_AE, "AE", "purple"),
    ]


class ACLTCPFlagMatchChoices(ChoiceSet):
    """
    How an ACL extended rule matches its selected TCP flags.
    """

    MATCH_ALL = "all"
    MATCH_ANY = "any"

    CHOICES = [
        (MATCH_ALL, "All", "blue"),
        (MATCH_ANY, "Any", "purple"),
    ]
