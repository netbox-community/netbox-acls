from utilities.choices import ChoiceSet

class ACLActionChoices(ChoiceSet):
    ACTION_DENY = 'deny'
    ACTION_PERMIT = 'permit'
    ACTION_REJECT = 'reject'

    CHOICES = [
        (ACTION_DENY, 'Deny', 'red'),
        (ACTION_PERMIT, 'Permit', 'green'),
        (ACTION_REJECT, 'Reject (Reset)', 'orange'),
    ]

class ACLRuleActionChoices(ChoiceSet):
    ACTION_DENY = 'deny'
    ACTION_PERMIT = 'permit'
    ACTION_REMARK = 'remark'

    CHOICES = [
        (ACTION_DENY, 'Deny', 'red'),
        (ACTION_PERMIT, 'Permit', 'green'),
        (ACTION_REMARK, 'Remark', 'blue'),
    ]

class ACLTypeChoices(ChoiceSet):

    CHOICES = [
        ('extended', 'Extended', 'purple'),
        ('standard', 'Standard', 'blue'),
    ]


class ACLProtocolChoices(ChoiceSet):

    CHOICES = [
        ('icmp', 'ICMP', 'purple'),
        ('tcp', 'TCP', 'blue'),
        ('udp', 'UDP', 'orange'),
    ]
