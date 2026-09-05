"""Declarative UI components for the plugin's detail views."""

from .attrs import AssignedObjectAttr, LogOptionsAttr, RuleCountAttr
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
    "LogOptionsAttr",
    "MemberTablePanel",
    "RuleCountAttr",
    "RuleTablePanel",
)
