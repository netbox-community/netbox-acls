"""
Filters enable users to request only a specific subset of objects matching a query;
when filtering the site list by status or region, for instance.
"""

import contextlib

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.filtersets import NetBoxModelFilterSet, PrimaryModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filters import ContentTypeFilter, MultiValueCharFilter, MultiValueNumberFilter
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
        if not value.strip():
            return queryset
        query = Q(name__icontains=value) | Q(description__icontains=value) | Q(comments__icontains=value)
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
    region_id = MultiValueNumberFilter(
        field_name="pk",
        method="filter_region",
        label=_("Region (ID)"),
    )
    region = MultiValueCharFilter(
        field_name="slug",
        method="filter_region",
        label=_("Region (slug)"),
    )
    site_group_id = MultiValueNumberFilter(
        field_name="pk",
        method="filter_site_group",
        label=_("Site group (ID)"),
    )
    site_group = MultiValueCharFilter(
        field_name="slug",
        method="filter_site_group",
        label=_("Site group (slug)"),
    )
    site_id = MultiValueNumberFilter(
        field_name="pk",
        method="filter_site",
        label=_("Site (ID)"),
    )
    site = MultiValueCharFilter(
        field_name="slug",
        method="filter_site",
        label=_("Site (slug)"),
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
        if not value.strip():
            return queryset
        query = (
            Q(access_list__name__icontains=value)
            | Q(interface__name__icontains=value)
            | Q(vminterface__name__icontains=value)
            | Q(device__name__icontains=value)
            | Q(virtual_chassis__name__icontains=value)
            | Q(virtual_machine__name__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(query)

    def _filter_scope(self, queryset, lookup, values):
        query = Q()
        for path in ACL_ASSIGNMENT_SITE_TRAVERSAL_PATHS:
            query |= Q(**{f"{path}__{lookup}__in": values})
        return queryset.filter(query).distinct()

    def _resolve_scope_objects(self, model, values):
        """
        Resolve slugs, then primary keys for values no slug claimed.

        The bare names took a primary key before 2.0.3. Numeric values still resolve so
        those callers keep working. Deprecated, and the fallback goes in the next major.
        """
        numeric = {}
        for value in values:
            # Not str.isdigit(): it accepts superscript digits that int() then rejects.
            try:
                pk = int(value)
            except ValueError:
                continue
            if pk > 0:
                numeric[value] = pk
        if not numeric:
            return model.objects.filter(slug__in=values)

        claimed = set(model.objects.filter(slug__in=list(numeric)).values_list("slug", flat=True))
        legacy = [pk for value, pk in numeric.items() if value not in claimed]
        if not legacy:
            return model.objects.filter(slug__in=values)
        return model.objects.filter(Q(slug__in=values) | Q(pk__in=legacy))

    def _filter_nested_scope(self, queryset, model, path, lookup, values):
        if lookup == "slug":
            objects = self._resolve_scope_objects(model, values)
        else:
            objects = model.objects.filter(pk__in=values)
        pks = set()
        for obj in objects:
            pks.update(obj.get_descendants(include_self=True).values_list("pk", flat=True))
        # A value matching no object has to match no assignment either.
        if not pks:
            return queryset.none()
        return self._filter_scope(queryset, f"{path}__pk", pks)

    def filter_site(self, queryset, name, value):
        """
        Match a site through every assignable target type.
        """
        if name == "slug":
            pks = self._resolve_scope_objects(Site, value).values_list("pk", flat=True)
            return self._filter_scope(queryset, "site__pk", list(pks))
        return self._filter_scope(queryset, f"site__{name}", value)

    def filter_region(self, queryset, name, value):
        """
        Match a region and everything below it in the tree.
        """
        return self._filter_nested_scope(queryset, Region, "site__region", name, value)

    def filter_site_group(self, queryset, name, value):
        """
        Match a site group and everything below it in the tree.
        """
        return self._filter_nested_scope(queryset, SiteGroup, "site__group", name, value)


class ACLRuleFilterSetMixin(django_filters.FilterSet):
    """
    Filters shared by both concrete ACL rule filter sets.
    """

    # Access List. The extended set overrides both to narrow them by ACL type.
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

    def search(self, queryset, name, value):
        """
        Override the default search behavior for the django model.
        """
        if not value.strip():
            return queryset
        query = (
            Q(access_list__name__icontains=value)
            | Q(remark__icontains=value)
            | Q(description__icontains=value)
            | Q(comments__icontains=value)
        )
        # Whole number, not a substring: q=1 must not return sequence 10.
        with contextlib.suppress(ValueError):
            query |= Q(sequence=int(value.strip()))
        return queryset.filter(query)


@register_filterset
class ACLStandardRuleFilterSet(ACLRuleFilterSetMixin, PrimaryModelFilterSet):
    """
    Define the filter set for the django model ACLStandardRule.
    """

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


@register_filterset
class ACLExtendedRuleFilterSet(ACLRuleFilterSetMixin, PrimaryModelFilterSet):
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
