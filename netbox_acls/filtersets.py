"""
Filters enable users to request only a specific subset of objects matching a query;
when filtering the site list by status or region, for instance.
"""

import django_filters
from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from ipam.models import Prefix
from netbox.filtersets import NetBoxModelFilterSet
from virtualization.models import VirtualMachine, VMInterface

from .choices import ACLTypeChoices
from .models import AccessList, ACLExtendedRule, ACLInterfaceAssignment, ACLStandardRule

__all__ = (
    "AccessListFilterSet",
    "ACLStandardRuleFilterSet",
    "ACLInterfaceAssignmentFilterSet",
    "ACLExtendedRuleFilterSet",
)


class AccessListFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model AccessList.
    """

    region = django_filters.ModelMultipleChoiceFilter(
        field_name="device__site__region",
        queryset=Region.objects.all(),
        to_field_name="id",
        label="Region",
    )
    site_group = django_filters.ModelMultipleChoiceFilter(
        field_name="device__site__group",
        queryset=SiteGroup.objects.all(),
        to_field_name="id",
        label="Site Group",
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name="device__site",
        queryset=Site.objects.all(),
        to_field_name="id",
        label="Site",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device",
        queryset=Device.objects.all(),
        label="Device (ID)",
    )
    virtual_chassis = django_filters.ModelMultipleChoiceFilter(
        field_name="virtual_chassis__name",
        queryset=VirtualChassis.objects.all(),
        to_field_name="name",
        label="Virtual Chassis (name)",
    )
    virtual_chassis_id = django_filters.ModelMultipleChoiceFilter(
        field_name="virtual_chassis",
        queryset=VirtualChassis.objects.all(),
        label="Virtual Chassis (ID)",
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name="virtual_machine__name",
        queryset=VirtualMachine.objects.all(),
        to_field_name="name",
        label="Virtual Machine (name)",
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name="virtual_machine",
        queryset=VirtualMachine.objects.all(),
        label="Virtual machine (ID)",
    )

    class Meta:
        """
        Associates the django model AccessList & fields to the filter set.
        """

        model = AccessList
        fields = (
            "id",
            "name",
            "device",
            "device_id",
            "virtual_chassis",
            "virtual_chassis_id",
            "virtual_machine",
            "virtual_machine_id",
            "type",
            "default_action",
            "comments",
            "site",
            "site_group",
            "region",
        )

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        query = (
            Q(name__icontains=value)
            | Q(device__name__icontains=value)
            | Q(virtual_chassis__name__icontains=value)
            | Q(virtual_machine__name__icontains=value)
            | Q(type__icontains=value)
            | Q(default_action__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(query)


class ACLInterfaceAssignmentFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLInterfaceAssignment.
    """

    access_list = django_filters.ModelMultipleChoiceFilter(
        queryset=AccessList.objects.all(),
        to_field_name="name",
        label=_("Access List (name)"),
    )
    access_list_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AccessList.objects.all(),
        to_field_name="id",
        label=_("Access List (ID)"),
    )
    interface = django_filters.ModelMultipleChoiceFilter(
        field_name="interface__name",
        queryset=Interface.objects.all(),
        to_field_name="name",
        label="Interface (name)",
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface",
        queryset=Interface.objects.all(),
        label="Interface (ID)",
    )
    vminterface = django_filters.ModelMultipleChoiceFilter(
        field_name="vminterface__name",
        queryset=VMInterface.objects.all(),
        to_field_name="name",
        label="VM Interface (name)",
    )
    vminterface_id = django_filters.ModelMultipleChoiceFilter(
        field_name="vminterface",
        queryset=VMInterface.objects.all(),
        label="VM Interface (ID)",
    )

    class Meta:
        """
        Associates the django model ACLInterfaceAssignment & fields to the filter set.
        """

        model = ACLInterfaceAssignment
        fields = (
            "id",
            "access_list",
            "direction",
            "interface",
            "interface_id",
            "vminterface",
            "vminterface_id",
        )

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        query = (
            Q(access_list__name__icontains=value)
            | Q(direction__icontains=value)
            | Q(interface__name__icontains=value)
            | Q(vminterface__name__icontains=value)
        )
        return queryset.filter(query)


class ACLStandardRuleFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLStandardRule.
    """

    # Access List
    access_list = django_filters.ModelMultipleChoiceFilter(
        queryset=AccessList.objects.all(),
        to_field_name="name",
        label=_("Access List (name)"),
    )
    access_list_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AccessList.objects.all(),
        to_field_name="id",
        label=_("Access List (ID)"),
    )

    # Source
    source_prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="source_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="name",
        label=_("Source Prefix (name)"),
    )
    source_prefix_id = django_filters.ModelMultipleChoiceFilter(
        field_name="source_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("Source Prefix (ID)"),
    )

    class Meta:
        """
        Associates the django model ACLStandardRule & fields to the filter set.
        """

        model = ACLStandardRule
        fields = ("id", "access_list", "index", "action")

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        query = (
            Q(access_list__name__icontains=value)
            | Q(index__icontains=value)
            | Q(action__icontains=value)
        )
        return queryset.filter(query)


class ACLExtendedRuleFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLExtendedRule.
    """

    # Access List
    access_list = django_filters.ModelMultipleChoiceFilter(
        queryset=AccessList.objects.filter(type=ACLTypeChoices.TYPE_EXTENDED),
        to_field_name="name",
        label=_("Access List (name)"),
    )
    access_list_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AccessList.objects.filter(type=ACLTypeChoices.TYPE_EXTENDED),
        to_field_name="id",
        label=_("Access List (ID)"),
    )

    # Source
    source_prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="source_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="name",
        label=_("Source Prefix (name)"),
    )
    source_prefix_id = django_filters.ModelMultipleChoiceFilter(
        field_name="source_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("Source Prefix (ID)"),
    )

    # Destination
    destination_prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="destination_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="name",
        label=_("Destination Prefix (name)"),
    )
    destination_prefix_id = django_filters.ModelMultipleChoiceFilter(
        field_name="destination_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("Destination Prefix (ID)"),
    )

    class Meta:
        """
        Associates the django model ACLExtendedRule & fields to the filter set.
        """

        model = ACLExtendedRule
        fields = ("id", "access_list", "index", "action", "protocol")

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        query = (
            Q(access_list__name__icontains=value)
            | Q(index__icontains=value)
            | Q(action__icontains=value)
            | Q(protocol__icontains=value)
        )
        return queryset.filter(query)
