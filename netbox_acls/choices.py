"""
Defines the various choices to be used by the models, forms, and other plugin specifics.
"""

from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

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
        Choice(
            ACTION_DENY,
            _("Deny"),
            color="red",
            description=_("Drop the traffic"),
        ),
        Choice(
            ACTION_PERMIT,
            _("Permit"),
            color="green",
            description=_("Allow the traffic"),
        ),
        Choice(
            ACTION_REJECT,
            _("Reject (Reset)"),
            color="orange",
            description=_("Drop the traffic and notify the sender"),
        ),
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
        Choice(FAMILY_IPV4, _("IPv4"), color="blue", description=_("IPv4 addresses only")),
        Choice(FAMILY_IPV6, _("IPv6"), color="purple", description=_("IPv6 addresses only")),
        Choice(FAMILY_DUAL, _("Dual"), color="cyan", description=_("IPv4 and IPv6 addresses")),
    ]


class ACLAddressFamilyChoices(ChoiceSet):
    """
    Single IP families supported by address groups.
    """

    key = "ACLAddressGroup.family"

    FAMILY_IPV4 = "ipv4"
    FAMILY_IPV6 = "ipv6"

    CHOICES = [
        Choice(FAMILY_IPV4, _("IPv4"), color="blue", description=_("IPv4 addresses only")),
        Choice(FAMILY_IPV6, _("IPv6"), color="purple", description=_("IPv6 addresses only")),
    ]


class ACLRuleActionChoices(ChoiceSet):
    """
    Defines the choices available for the Access Lists plugin specific to ACL rule actions.
    """

    ACTION_DENY = "deny"
    ACTION_PERMIT = "permit"
    ACTION_REMARK = "remark"

    CHOICES = [
        Choice(ACTION_DENY, _("Deny"), color="red", description=_("Drop the traffic")),
        Choice(ACTION_PERMIT, _("Permit"), color="green", description=_("Allow the traffic")),
        Choice(ACTION_REMARK, _("Remark"), color="blue", description=_("A comment with no match criteria")),
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
            _("Generic"),
            (
                Choice(
                    OPTION_SYSLOG,
                    _("Syslog"),
                    color="blue",
                    description=_("Send log messages to syslog"),
                ),
            ),
        ),
        (
            _("Cisco"),
            (
                Choice(
                    OPTION_CISCO_LOG_INPUT,
                    _("Log-input"),
                    color="purple",
                    description=_("Include the input interface and source MAC address when available"),
                ),
            ),
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
        (USAGE_SOURCE, _("Source"), "blue"),
        (USAGE_DESTINATION, _("Destination"), "purple"),
        (USAGE_BOTH, _("Source and destination"), "teal"),
    ]


class ACLAssignmentDirectionUIChoices(ChoiceSet):
    """
    Defines the application direction of the ACL on an associated interface (UI version).
    """

    DIRECTION_INGRESS = "ingress"
    DIRECTION_EGRESS = "egress"

    CHOICES = [
        Choice(DIRECTION_INGRESS, _("Ingress"), color="blue", description=_("Traffic entering the interface")),
        Choice(DIRECTION_EGRESS, _("Egress"), color="purple", description=_("Traffic leaving the interface")),
    ]


class ACLAssignmentDirectionChoices(ChoiceSet):
    """
    Defines the application direction of the ACL on an associated interface.
    """

    DIRECTION_INGRESS = "ingress"
    DIRECTION_EGRESS = "egress"
    DIRECTION_NONE = "none"

    CHOICES = [
        (DIRECTION_INGRESS, _("Ingress"), "blue"),
        (DIRECTION_EGRESS, _("Egress"), "purple"),
        (DIRECTION_NONE, _("N/A"), "darkgray"),
    ]


class ACLTypeChoices(ChoiceSet):
    """
    Defines the choices available for the Access Lists plugin specific to ACL type.
    """

    TYPE_STANDARD = "standard"
    TYPE_EXTENDED = "extended"

    CHOICES = [
        Choice(
            TYPE_EXTENDED,
            _("Extended"),
            color="purple",
            description=_("Matches source, destination and protocol criteria"),
        ),
        Choice(
            TYPE_STANDARD,
            _("Standard"),
            color="blue",
            description=_("Matches the source only"),
        ),
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
            _("Common"),
            (
                Choice(
                    PROTOCOL_ICMP,
                    _("ICMP"),
                    color="purple",
                    description=_("Follows the ACL or address family"),
                ),
                Choice(
                    PROTOCOL_ICMPV4,
                    _("ICMPv4"),
                    color="purple",
                    description=_("Always IPv4, IP protocol 1"),
                ),
                Choice(
                    PROTOCOL_ICMPV6,
                    _("ICMPv6"),
                    color="purple",
                    description=_("Always IPv6, IP protocol 58"),
                ),
                Choice(
                    PROTOCOL_IP,
                    _("IP"),
                    color="cyan",
                    description=_("Any IP protocol"),
                ),
                Choice(
                    PROTOCOL_TCP,
                    _("TCP"),
                    color="blue",
                    description=_("Transmission Control Protocol, IP protocol 6"),
                ),
                Choice(
                    PROTOCOL_UDP,
                    _("UDP"),
                    color="orange",
                    description=_("User Datagram Protocol, IP protocol 17"),
                ),
            ),
        ),
        (
            _("Routing and tunneling"),
            (
                Choice(
                    PROTOCOL_GRE,
                    _("GRE"),
                    color="teal",
                    description=_("Generic Routing Encapsulation, IP protocol 47"),
                ),
                Choice(
                    PROTOCOL_EIGRP,
                    _("EIGRP"),
                    color="yellow",
                    description=_("Enhanced Interior Gateway Routing Protocol, IP protocol 88"),
                ),
                Choice(
                    PROTOCOL_OSPF,
                    _("OSPF"),
                    color="green",
                    description=_("Open Shortest Path First, IP protocol 89"),
                ),
                Choice(
                    PROTOCOL_PIM,
                    _("PIM"),
                    color="indigo",
                    description=_("Protocol Independent Multicast, IP protocol 103"),
                ),
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
        (TYPE_ECHO_REPLY, _("Echo reply (0)")),
        (TYPE_DESTINATION_UNREACHABLE, _("Destination unreachable (3)")),
        (TYPE_REDIRECT, _("Redirect (5)")),
        (TYPE_ECHO_REQUEST, _("Echo request (8)")),
        (TYPE_ROUTER_ADVERTISEMENT, _("Router advertisement (9)")),
        (TYPE_ROUTER_SOLICITATION, _("Router solicitation (10)")),
        (TYPE_TIME_EXCEEDED, _("Time exceeded (11)")),
        (TYPE_PARAMETER_PROBLEM, _("Parameter problem (12)")),
        (TYPE_TIMESTAMP, _("Timestamp (13)")),
        (TYPE_TIMESTAMP_REPLY, _("Timestamp reply (14)")),
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
        (TYPE_DESTINATION_UNREACHABLE, _("Destination unreachable (1)")),
        (TYPE_PACKET_TOO_BIG, _("Packet too big (2)")),
        (TYPE_TIME_EXCEEDED, _("Time exceeded (3)")),
        (TYPE_PARAMETER_PROBLEM, _("Parameter problem (4)")),
        (TYPE_ECHO_REQUEST, _("Echo request (128)")),
        (TYPE_ECHO_REPLY, _("Echo reply (129)")),
        (TYPE_MULTICAST_LISTENER_QUERY, _("Multicast listener query (130)")),
        (TYPE_MULTICAST_LISTENER_REPORT, _("Multicast listener report (131)")),
        (TYPE_MULTICAST_LISTENER_DONE, _("Multicast listener done (132)")),
        (TYPE_ROUTER_SOLICITATION, _("Router solicitation (133)")),
        (TYPE_ROUTER_ADVERTISEMENT, _("Router advertisement (134)")),
        (TYPE_NEIGHBOR_SOLICITATION, _("Neighbor solicitation (135)")),
        (TYPE_NEIGHBOR_ADVERTISEMENT, _("Neighbor advertisement (136)")),
        (TYPE_REDIRECT, _("Redirect (137)")),
        (TYPE_MULTICAST_LISTENER_REPORT_V2, _("Multicast listener report v2 (143)")),
    ]


class ACLICMPTypeChoices(ChoiceSet):
    """
    ICMPv4 and ICMPv6 type presets in one list, labelled with their family.
    """

    # Flat, since the preset widget renders no option groups.
    CHOICES = [
        *((value, format_lazy("ICMPv4: {}", label)) for value, label in ACLICMPv4TypeChoices.CHOICES),
        *((value, format_lazy("ICMPv6: {}", label)) for value, label in ACLICMPv6TypeChoices.CHOICES),
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
        Choice(FLAG_FIN, _("FIN"), color="orange", description=_("No more data from the sender")),
        Choice(FLAG_SYN, _("SYN"), color="green", description=_("Synchronize sequence numbers")),
        Choice(FLAG_RST, _("RST"), color="red", description=_("Reset the connection")),
        Choice(FLAG_PSH, _("PSH"), color="cyan", description=_("Push buffered data to the application")),
        Choice(FLAG_ACK, _("ACK"), color="blue", description=_("Acknowledgment field is significant")),
        Choice(FLAG_URG, _("URG"), color="yellow", description=_("Urgent pointer field is significant")),
        Choice(FLAG_ECE, _("ECE"), color="teal", description=_("ECN-Echo")),
        Choice(FLAG_CWR, _("CWR"), color="indigo", description=_("Congestion window reduced")),
        Choice(FLAG_AE, _("AE"), color="purple", description=_("Accurate ECN, formerly NS")),
    ]


class ACLTCPFlagMatchChoices(ChoiceSet):
    """
    How an ACL extended rule matches its selected TCP flags.
    """

    MATCH_ALL = "all"
    MATCH_ANY = "any"

    CHOICES = [
        Choice(MATCH_ALL, _("All"), color="blue", description=_("Every selected flag is set")),
        Choice(MATCH_ANY, _("Any"), color="purple", description=_("At least one selected flag is set")),
    ]
