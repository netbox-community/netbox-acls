"""
Search definitions for models in the application.

This module defines search indices for models, enabling advanced search
functionalities and configurations for the corresponding models.
"""

from netbox.search import SearchIndex, register_search

from .models.access_list_rules import ACLExtendedRule, ACLStandardRule
from .models.access_lists import AccessList


@register_search
class AccessListIndex(SearchIndex):
    """
    NetBox search definition for the AccessList model.
    """

    model = AccessList

    fields: tuple = (
        ("name", 100),
        ("comments", 5000),
    )
    display_attrs: tuple = (
        "name",
        "type",
        "default_action",
    )


@register_search
class ACLStandardRuleIndex(SearchIndex):
    """
    NetBox search definition for the ACLStandardRule model.
    """

    model = ACLStandardRule

    fields: tuple = (
        ("remark", 400),
        ("description", 500),
    )
    display_attrs: tuple = (
        "access_list",
        "sequence",
        "description",
        "action",
        "remark",
        "source_type",
        "source",
    )


@register_search
class ACLExtendedRuleIndex(SearchIndex):
    """
    NetBox search definition for the ACLExtendedRule model.
    """

    model = ACLExtendedRule

    fields: tuple = (
        ("remark", 400),
        ("description", 500),
    )
    display_attrs: tuple = (
        "access_list",
        "sequence",
        "action",
        "remark",
        "protocol",
        "source_type",
        "source",
        "source_ports",
        "destination",
        "destination_type",
        "destination_ports",
    )
