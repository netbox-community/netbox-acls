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
    "ACLProtocolChoices",
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

    CHOICES = [
        ("ingress", "Ingress", "blue"),
        ("egress", "Egress", "purple"),
    ]


class ACLTypeChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL type.
    """

    CHOICES = [
        ("extended", "Extended", "purple"),
        ("standard", "Standard", "blue"),
    ]


class ACLProtocolChoices(ChoiceSet):
    """
    Defines the choices availble for the Access Lists plugin specific to ACL Rule protocol.
    """

    CHOICES = [
        ("icmp", "ICMP", "purple"),
        ("tcp", "TCP", "blue"),
        ("udp", "UDP", "orange"),
    ]
