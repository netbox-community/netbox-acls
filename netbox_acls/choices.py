"""
Defines the various choices to be used by the models, forms, and other plugin specifics.
"""

from utilities.choices import ChoiceSet

__all__ = (
    "ACLActionChoices",
    "ACLAssignmentDirectionChoices",
    "ACLProtocolChoices",
    "ACLRuleActionChoices",
    "ACLTypeChoices",
    "ACLICMPTypeChoices",
    "ACLTCPFlagsChoices",
)


class ACLActionChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL default_action.
    """

    ACTION_DENY = "deny"
    ACTION_PERMIT = "permit"
    ACTION_REJECT = "reject"

    CHOICES = [
        (ACTION_DENY, "Deny", "red"),
        (ACTION_PERMIT, "Permit", "green"),
        (ACTION_REJECT, "Reject (Reset)", "orange"),
    ]


class ACLRuleActionChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL rule actions.
    """

    ACTION_DENY = "deny"
    ACTION_PERMIT = "permit"
    ACTION_REMARK = "remark"

    CHOICES = [
        (ACTION_DENY, "Deny", "red"),
        (ACTION_PERMIT, "Permit", "green"),
        (ACTION_REMARK, "Remark", "blue"),
    ]


class ACLAssignmentDirectionChoices(ChoiceSet):
    """
    Defines the direction of the application of the ACL on an associated interface.
    """

    DIRECTION_INGRESS = "ingress"
    DIRECTION_EGRESS = "egress"

    CHOICES = [
        (DIRECTION_INGRESS, "Ingress", "blue"),
        (DIRECTION_EGRESS, "Egress", "purple"),
    ]


class ACLTypeChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL type.
    """

    TYPE_STANDARD = "standard"
    TYPE_EXTENDED = "extended"

    CHOICES = [
        (TYPE_EXTENDED, "Extended", "purple"),
        (TYPE_STANDARD, "Standard", "blue"),
    ]


class ACLProtocolChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL Rule protocol.
    """

    PROTOCOL_ICMP = "icmp"
    PROTOCOL_TCP = "tcp"
    PROTOCOL_UDP = "udp"
    PROTOCOL_IP = "ip"

    CHOICES = [
        (PROTOCOL_ICMP, "ICMP", "purple"),
        (PROTOCOL_TCP, "TCP", "blue"),
        (PROTOCOL_UDP, "UDP", "orange"),
        (PROTOCOL_IP, "IP", "green"),
    ]

    
class ACLIPFlagsChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL IP header flags. Excluding the Reserved Flag.
    """
    
    IPFlag_DF = "ipdf"
    IPFlag_MF = "ipmf"
    
    CHOICES = [
         (IPFlag_DF, "IP Do not Fragment", "yellow")
         (IPFlag_MF, "IP More Fragments", "yellow")
    ]  
 
          
class ACLTCPFlagsChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL TCP protocol flags.
    """
    
    TCPFlag_CWR = "cwr"
    TCPFlag_ECE = "ece"
    TCPFlag_URG = "urg"
    TCPFlag_ACK = "ack"
    TCPFlag_PSH = "psh"
    TCPFlag_RST = "rst"
    TCPFlag_SYN = "syn"
    TCPFlag_FIN = "fin"
    
    CHOICES = [
        (TCPFlag_CWR, "CWR", "blue")
        (TCPFlag_ECE, "ECE", "blue")
        (TCPFlag_URG, "URG", "orage")
        (TCPFlag_ACK, "ACK", "green")
        (TCPFlag_PSH, "PSH", "green")
        (TCPFlag_RST, "RST", "red")
        (TCPFlag_SYN, "SYN", "blue")
        (TCPFlag_FIN, "FIN", "red")   
    ]

          
class ACLICMPTypeChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL ICMP Types. Includes Deprecated flags with a "_d" suffix. Unassigned Types are left out.
    """
    
    ICMPType0 = "echo_reply"
    ICMPType3 = "dst_unreachable"
    ICMPType4 = "src_quench_d"
    ICMPType5 = "redirect"
    ICMPType6 = "alt_host_address_d"
    ICMPType8 = "echo"
    ICMPType9 = "router_advertisement"
    ICMPType10 = "router_selection"
    ICMPType11 = "time_exceeded"
    ICMPType12 = "parameter_problem"
    ICMPType13 = "timestamp"
    ICMPType14 = "timestamp_reply"
    ICMPType15 = "info_request_d"
    ICMPType16 = "info_reply_d"
    ICMPType17 = "addr_mask_request_d"
    ICMPType18 = "addr_mask_reply_d"
    ICMPType19 = "reserved_security"
    ICMPType20 = "reserved_robustness_experiment"
    ICMPType21 = "reserved_robustness_experiment"
    ICMPType22 = "reserved_robustness_experiment"
    ICMPType23 = "reserved_robustness_experiment"
    ICMPType24 = "reserved_robustness_experiment"
    ICMPType25 = "reserved_robustness_experiment"
    ICMPType26 = "reserved_robustness_experiment"
    ICMPType27 = "reserved_robustness_experiment"
    ICMPType28 = "reserved_robustness_experiment"
    ICMPType29 = "reserved_robustness_experiment"
    ICMPType30 = "traceroute_d"
    ICMPType31 = "datagram_conversion_error_d"
    ICMPType32 = "mobile_host_redirect_d"
    ICMPType33 = "ipv6_where_are_you_d"
    ICMPType34 = "ipv6_i_am_here_d"
    ICMPType35 = "mobile_registration_req_d"
    ICMPType36 = "mobile_registration_reply_d"
    ICMPType37 = "domain_name_req_d"
    ICMPType38 = "domain_name_reply_d"
    ICMPType39 = "skip_d"
    ICMPType40 = "photuris"
    ICMPType41 = "experimental_mobility_protocols"
    ICMPType42 = "extended_echo_request"
    ICMPType43 = "extended_echo_reply"
    ICMPType253 = "rfc3692-style_experiment_1"
    ICMPType254 = "rfc3692-style_experiment_2"
    
    CHOICES = [
        (ICMPType0, "Echo Reply", "green")
        (ICMPType3, "Destination Unreachable", "green")
        (ICMPType4, "Source Quench Deprecated", "red")
        (ICMPType5, "Redirect", "yellow")
        (ICMPType6, "Alternative Host Address Deprecated", "red")
        (ICMPType8, "Echo", "green")
        (ICMPType9, "Router Advertisement", "yellow")
        (ICMPType10, "Router Selection", "yellow")
        (ICMPType11, "Time Exceeded", "green")
        (ICMPType12, "Parameter Problem", "yellow")
        (ICMPType13, "Timestamp", "yellow")
        (ICMPType14, "Timestamp Reply", "yellow")
        (ICMPType15, "Info Request Deprecated", "red")
        (ICMPType16, "Info Reply Deprecated", "red")
        (ICMPType17, "Address Mask Request Deprecated", "red")
        (ICMPType18, "Address Mask Reply Deprecated", "red")
        (ICMPType19, "Reserved for Security", "yellow")
        (ICMPType20, "Reserved  Robustness Experiment", "yellow")
        (ICMPType21, "Reserved  Robustness Experiment", "yellow")
        (ICMPType22, "Reserved  Robustness Experiment", "yellow")
        (ICMPType23, "Reserved  Robustness Experiment", "yellow")
        (ICMPType24, "Reserved  Robustness Experiment", "yellow")
        (ICMPType25, "Reserved  Robustness Experiment", "yellow")
        (ICMPType26, "Reserved  Robustness Experiment", "yellow")
        (ICMPType27, "Reserved  Robustness Experiment", "yellow")
        (ICMPType28, "Reserved  Robustness Experiment", "yellow")
        (ICMPType29, "Reserved  Robustness Experiment", "yellow")
        (ICMPType30, "Traceroute Deprecated", "red")
        (ICMPType31, "Datagram Conversion Error Deprecated", "red")
        (ICMPType32, "Mobile Host Redirect Deprecated", "red")
        (ICMPType33, "IPv6 Where are You Deprecated", "red")
        (ICMPType34, "IPv6 I am Here Deprecated", "red")
        (ICMPType35, "Mobile Registration Request Deprecated", "red")
        (ICMPType36, "Mobile Registration_Reply Deprecated", "red")
        (ICMPType37, "Domain Name Request Deprecated", "red")
        (ICMPType38, "Domain Name Reply Deprecated", "red")
        (ICMPType39, "SKIP Deprecated", "red")
        (ICMPType40, "Photuris", "yellow")
        (ICMPType41, "Experimental Mobility Protocols", "yellow")
        (ICMPType42, "Extended Echo Request", "green")
        (ICMPType43, "Extended Echo Reply", "green")
        (ICMPType253, "RFC3692-style Experiment 1", "yellow")
        (ICMPType254, "RFC3692-style Experiment 2", "yellow")
    ]
