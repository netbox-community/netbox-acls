"""
Filters enable users to request only a specific subset of objects matching a query;
when filtering the sites list by status or region, for instance.
"""
import django_filters
from dcim.models import Device, Interface, VirtualChassis
from netbox.filtersets import NetBoxModelFilterSet
from virtualization.models import VirtualMachine, VMInterface

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
        )

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        return queryset.filter(description__icontains=value)


class ACLInterfaceAssignmentFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLInterfaceAssignment.
    """

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
        return queryset.filter(description__icontains=value)


class ACLStandardRuleFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLStandardRule.
    """

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
        return queryset.filter(description__icontains=value)


class ACLExtendedRuleFilterSet(NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLExtendedRule.
    """

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
        return queryset.filter(description__icontains=value)
