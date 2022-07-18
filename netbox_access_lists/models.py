from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet


class ACLActionChoices(ChoiceSet):
    key = 'ACLExtendedRule.action'
    ACTION_DENY = 'deny'
    ACTION_PERMIT = 'permit'
    ACTION_REJECT = 'reject'

    CHOICES = [
        (ACTION_DENY, 'Deny', 'red'),
        (ACTION_PERMIT, 'Permit', 'green'),
        (ACTION_REJECT, 'Reject (Reset)', 'orange'),
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


class AccessList(NetBoxModel):
    name = models.CharField(
        max_length=100
    )
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='access_lists'
    )
    type = models.CharField(
        max_length=30,
        choices=ACLTypeChoices
    )
    default_action = models.CharField(
        default=ACLActionChoices.ACTION_DENY,
        max_length=30,
        choices=ACLActionChoices,
        verbose_name='Default Action'
    )
    comments = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ('name', 'device')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_access_lists:accesslist', args=[self.pk])

    def get_default_action_color(self):
        return ACLActionChoices.colors.get(self.default_action)

    def get_type_color(self):
        return ACLTypeChoices.colors.get(self.type)


class ACLRule(NetBoxModel):
    """
    Abstract model for ACL Rules.
    """
    access_list = models.ForeignKey(
        on_delete=models.CASCADE,
        to=AccessList,
        verbose_name='Access-List',
    )
    index = models.PositiveIntegerField()
    remark = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    action = models.CharField(
        blank=True,
        null=True,
        choices=ACLActionChoices,
        max_length=30,
    )
    source_prefix = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
        to='ipam.Prefix',
        verbose_name='Source Prefix'
    )

    def __str__(self):
        return f'{self.access_list}: Rule {self.index}'

    def get_action_color(self):
        return ACLActionChoices.colors.get(self.action)


    class Meta:
        abstract = True
        default_related_name='%(class)ss'
        ordering = ('access_list', 'index')
        unique_together = ('access_list', 'index')


class ACLStandardRule(ACLRule):

    def get_absolute_url(self):
        return reverse('plugins:netbox_access_lists:aclstandardrule', args=[self.pk])


class ACLExtendedRule(ACLRule):
    source_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        blank=True,
        null=True,
        verbose_name='Soure Ports'
    )
    destination_prefix = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
        to='ipam.Prefix',
        verbose_name='Destination Prefix'
    )
    destination_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        blank=True,
        null=True,
        verbose_name='Destination Ports'
    )
    protocol = models.CharField(
        blank=True,
        choices=ACLProtocolChoices,
        max_length=30,
    )

    def get_absolute_url(self):
        return reverse('plugins:netbox_access_lists:aclextendedrule', args=[self.pk])

    def get_protocol_color(self):
        return ACLProtocolChoices.colors.get(self.protocol)
