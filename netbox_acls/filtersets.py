"""
Filters enable users to request only a specific subset of objects matching a query;
when filtering the site list by status or region, for instance.
"""

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.filtersets import NetBoxModelFilterSet, PrimaryModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filters import ContentTypeFilter
from utilities.filtersets import register_filterset
from virtualization.models import VirtualMachine, VMInterface

from .choices import ACLTypeChoices
from .constants import ACL_ASSIGNMENT_SITE_TRAVERSAL_PATHS
from .models import AccessList, ACLAssignment, ACLExtendedRule, ACLStandardRule

__all__ = (
    "ACLAssignmentFilterSet",
    "ACLExtendedRuleFilterSet",
    "ACLStandardRuleFilterSet",
    "AccessListFilterSet",
)


@register_filterset
class AccessListFilterSet(PrimaryModelFilterSet):
    """
    Define the filter set for the django model AccessList.
    """

    class Meta:
        """
        Associates the django model AccessList & fields with the filter set.
        """

        model = AccessList
        fields = (
            "id",
            "name",
            "type",
            "family",
            "default_action",
            "description",
            "comments",
        )

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        query = (
            Q(name__icontains=value)
            | Q(type__icontains=value)
            | Q(default_action__icontains=value)
            | Q(description__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(query)


@register_filterset
class ACLAssignmentFilterSet(OwnerFilterMixin, NetBoxModelFilterSet):
    """
    Define the filter set for the django model ACLAssignment.
    """

    # Access List
    access_list = django_filters.ModelMultipleChoiceFilter(
        field_name="access_list__name",
        queryset=AccessList.objects.all(),
        to_field_name="name",
        label=_("Access List (name)"),
    )
    access_list_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AccessList.objects.all(),
        to_field_name="id",
        label=_("Access List (ID)"),
    )

    # Organization
    region_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site__region",
        queryset=Region.objects.all(),
        method="filter_nested_scope",
        label=_("Region (ID)"),
    )
    region = django_filters.ModelMultipleChoiceFilter(
        field_name="site__region",
        queryset=Region.objects.all(),
        method="filter_nested_scope",
        label=_("Region (ID)"),
    )
    site_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site__group",
        queryset=SiteGroup.objects.all(),
        method="filter_nested_scope",
        label=_("Site group (ID)"),
    )
    site_group = django_filters.ModelMultipleChoiceFilter(
        field_name="site__group",
        queryset=SiteGroup.objects.all(),
        method="filter_nested_scope",
        label=_("Site group (ID)"),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site",
        queryset=Site.objects.all(),
        method="filter_scope",
        label=_("Site (ID)"),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name="site",
        queryset=Site.objects.all(),
        method="filter_scope",
        label=_("Site (ID)"),
    )

    # Device
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

    # Interface
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

    # Virtual Chassis
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

    # Virtual Machine
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

    # Virtual Machine Interface
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
        Associates the django model ACLInterfaceAssignment & fields with the filter set.
        """

        model = ACLAssignment
        fields = (
            "id",
            "access_list",
            "family",
            "site",
            "site_id",
            "site_group",
            "site_group_id",
            "region",
            "region_id",
            "device",
            "device_id",
            "virtual_chassis",
            "virtual_chassis_id",
            "virtual_machine",
            "virtual_machine_id",
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
            | Q(device__name__icontains=value)
            | Q(virtual_chassis__name__icontains=value)
            | Q(virtual_machine__name__icontains=value)
        )
        return queryset.filter(query)

    def _filter_scope(self, queryset, lookup, pks):
        # FilterMethod's own guard misses this: an empty queryset is not in EMPTY_VALUES.
        if not pks:
            return queryset
        query = Q()
        for path in ACL_ASSIGNMENT_SITE_TRAVERSAL_PATHS:
            query |= Q(**{f"{path}__{lookup}__in": pks})
        return queryset.filter(query).distinct()

    def filter_scope(self, queryset, name, value):
        """
        Match a scope object through every assignable target type.
        """
        return self._filter_scope(queryset, name, {obj.pk for obj in value})

    def filter_nested_scope(self, queryset, name, value):
        """
        Match a nested scope object and everything below it in the tree.
        """
        pks = set()
        for obj in value:
            pks.update(obj.get_descendants(include_self=True).values_list("pk", flat=True))
        return self._filter_scope(queryset, name, pks)


@register_filterset
class ACLStandardRuleFilterSet(PrimaryModelFilterSet):
    """
    Define the filter set for the django model ACLStandardRule.
    """

    # Access List
    access_list = django_filters.ModelMultipleChoiceFilter(
        field_name="access_list__name",
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
    source_type = ContentTypeFilter(
        label=_("Source Type"),
    )
    source_aggregate = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_aggregate__prefix",
        queryset=Aggregate.objects.all(),
        to_field_name="prefix",
        label=_("Source Aggregate (name)"),
    )
    source_aggregate_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_aggregate",
        queryset=Aggregate.objects.all(),
        to_field_name="id",
        label=_("Source Aggregate (ID)"),
    )
    source_ipaddress = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_ipaddress__address",
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        label=_("Source IP-Address (name)"),
    )
    source_ipaddress_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_ipaddress",
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label=_("Source IP-Address (ID)"),
    )
    source_iprange = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_iprange__start_address",
        queryset=IPRange.objects.all(),
        to_field_name="start_address",
        label=_("Source IP-Range (name)"),
    )
    source_iprange_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_iprange",
        queryset=IPRange.objects.all(),
        to_field_name="id",
        label=_("Source IP-Range (ID)"),
    )
    source_prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_prefix__prefix",
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        label=_("Source Prefix (name)"),
    )
    source_prefix_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("Source Prefix (ID)"),
    )

    class Meta:
        """
        Associates the django model ACLStandardRule & fields with the filter set.
        """

        model = ACLStandardRule
        fields = (
            "id",
            "access_list",
            "sequence",
            "action",
            "remark",
            "source_type",
            "source_id",
            "description",
            "comments",
        )

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        query = (
            Q(access_list__name__icontains=value)
            | Q(sequence__icontains=value)
            | Q(action__icontains=value)
            | Q(remark__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(query)


@register_filterset
class ACLExtendedRuleFilterSet(PrimaryModelFilterSet):
    """
    Define the filter set for the django model ACLExtendedRule.
    """

    # Access List
    access_list = django_filters.ModelMultipleChoiceFilter(
        field_name="access_list__name",
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
    source_type = ContentTypeFilter(
        label=_("Source Type"),
    )
    source_aggregate = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_aggregate__prefix",
        queryset=Aggregate.objects.all(),
        to_field_name="prefix",
        label=_("Source Aggregate (name)"),
    )
    source_aggregate_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_aggregate",
        queryset=Aggregate.objects.all(),
        to_field_name="id",
        label=_("Source Aggregate (ID)"),
    )
    source_ipaddress = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_ipaddress__address",
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        label=_("Source IP-Address (name)"),
    )
    source_ipaddress_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_ipaddress",
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label=_("Source IP-Address (ID)"),
    )
    source_iprange = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_iprange__start_address",
        queryset=IPRange.objects.all(),
        to_field_name="start_address",
        label=_("Source IP-Range (name)"),
    )
    source_iprange_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_iprange",
        queryset=IPRange.objects.all(),
        to_field_name="id",
        label=_("Source IP-Range (ID)"),
    )
    source_prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_prefix__prefix",
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        label=_("Source Prefix (name)"),
    )
    source_prefix_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_source_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("Source Prefix (ID)"),
    )
    source_port = django_filters.NumberFilter(
        field_name="source_port_ranges",
        lookup_expr="range_contains",
        label=_("Source Port"),
    )

    # Destination
    destination_type = ContentTypeFilter(
        label=_("Destination Type"),
    )
    destination_aggregate = django_filters.ModelMultipleChoiceFilter(
        field_name="_destination_aggregate__prefix",
        queryset=Aggregate.objects.all(),
        to_field_name="prefix",
        label=_("Destination Aggregate (name)"),
    )
    destination_aggregate_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_destination_aggregate",
        queryset=Aggregate.objects.all(),
        to_field_name="id",
        label=_("Destination Aggregate (ID)"),
    )
    destination_ipaddress = django_filters.ModelMultipleChoiceFilter(
        field_name="_destination_ipaddress__address",
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        label=_("Destination IP-Address (name)"),
    )
    destination_ipaddress_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_destination_ipaddress",
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label=_("Destination IP-Address (ID)"),
    )
    destination_iprange = django_filters.ModelMultipleChoiceFilter(
        field_name="_destination_iprange__start_address",
        queryset=IPRange.objects.all(),
        to_field_name="start_address",
        label=_("Destination IP-Range (name)"),
    )
    destination_iprange_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_destination_iprange",
        queryset=IPRange.objects.all(),
        to_field_name="id",
        label=_("Destination IP-Range (ID)"),
    )
    destination_prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="_destination_prefix__prefix",
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        label=_("Destination Prefix (name)"),
    )
    destination_prefix_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_destination_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("Destination Prefix (ID)"),
    )
    destination_port = django_filters.NumberFilter(
        field_name="destination_port_ranges",
        lookup_expr="range_contains",
        label=_("Destination Port"),
    )

    class Meta:
        """
        Associates the django model ACLExtendedRule & fields with the filter set.
        """

        model = ACLExtendedRule
        fields = (
            "id",
            "access_list",
            "sequence",
            "action",
            "remark",
            "protocol",
            "source_type",
            "source_id",
            "source_port",
            "destination_type",
            "destination_id",
            "destination_port",
            "description",
            "comments",
        )

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        query = (
            Q(access_list__name__icontains=value)
            | Q(sequence__icontains=value)
            | Q(action__icontains=value)
            | Q(remark__icontains=value)
            | Q(protocol__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(query)
