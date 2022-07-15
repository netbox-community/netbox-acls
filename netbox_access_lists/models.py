from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet


class AccessListActionChoices(ChoiceSet):
    key = 'AccessListRule.action'
    ACTION_DENY = 'deny'
    ACTION_PERMIT = 'permit'
    ACTION_REJECT = 'reject'

    CHOICES = [
        (ACTION_DENY, 'Deny', 'red'),
        (ACTION_PERMIT, 'Permit', 'green'),
        (ACTION_REJECT, 'Reject (Reset)', 'orange'),
    ]


class AccessListTypeChoices(ChoiceSet):

    CHOICES = [
        ('extended', 'Extended', 'purple'),
        ('standard', 'Standard', 'blue'),
    ]


class AccessListProtocolChoices(ChoiceSet):

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
        choices=AccessListTypeChoices
    )
    default_action = models.CharField(
        default=AccessListActionChoices.ACTION_DENY,
        max_length=30,
        choices=AccessListActionChoices
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
        return AccessListActionChoices.colors.get(self.default_action)

    def get_type_color(self):
        return AccessListTypeChoices.colors.get(self.type)


class AccessListRule(NetBoxModel):
    access_list = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name='rules',
        to=AccessList,
    )
    index = models.PositiveIntegerField()
    protocol = models.CharField(
        blank=True,
        choices=AccessListProtocolChoices,
        max_length=30,
    )
    source_prefix = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
        to='ipam.Prefix',
    )
    source_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        blank=True,
        null=True,
    )
    destination_prefix = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
        to='ipam.Prefix',
    )
    destination_ports = ArrayField(
        base_field=models.PositiveIntegerField(),
        blank=True,
        null=True,
    )
    action = models.CharField(
        choices=AccessListActionChoices,
        default=AccessListActionChoices.ACTION_PERMIT,
        max_length=30,
    )
    remark = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('access_list', 'index')
        unique_together = ('access_list', 'index')

    def __str__(self):
        return f'{self.access_list}: Rule {self.index}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_access_lists:accesslistrule', args=[self.pk])

    def get_protocol_color(self):
        return AccessListProtocolChoices.colors.get(self.protocol)

    def get_action_color(self):
        return AccessListActionChoices.colors.get(self.action)
