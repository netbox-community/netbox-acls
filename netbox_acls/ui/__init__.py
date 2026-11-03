"""Declarative UI components for the plugin's detail views."""

from .attrs import AssignedObjectAttr, BadgesAttr, RuleCountAttr
from .panels import (
    AccessListPanel,
    ACLAddressGroupMemberPanel,
    ACLAddressGroupPanel,
    ACLAssignmentPanel,
    ACLExtendedRuleDetailsPanel,
    ACLExtendedRulePanel,
    ACLRuleLoggingPanel,
    ACLStandardRuleDetailsPanel,
    ACLStandardRulePanel,
    MemberTablePanel,
    RuleTablePanel,
)

__all__ = (
    "ACLAddressGroupMemberPanel",
    "ACLAddressGroupPanel",
    "ACLAssignmentPanel",
    "ACLExtendedRuleDetailsPanel",
    "ACLExtendedRulePanel",
    "ACLRuleLoggingPanel",
    "ACLStandardRuleDetailsPanel",
    "ACLStandardRulePanel",
    "AccessListPanel",
    "AssignedObjectAttr",
    "BadgesAttr",
    "MemberTablePanel",
    "RuleCountAttr",
    "RuleTablePanel",
)
