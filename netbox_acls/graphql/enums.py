import strawberry

from ..choices import (
    ACLActionChoices,
    ACLAddressFamilyChoices,
    ACLAssignmentDirectionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)

__all__ = (
    "ACLActionEnum",
    "ACLAddressFamilyEnum",
    "ACLAssignmentDirectionEnum",
    "ACLFamilyEnum",
    "ACLProtocolEnum",
    "ACLRuleActionEnum",
    "ACLTypeEnum",
)

#
# Access List
#

ACLActionEnum = strawberry.enum(ACLActionChoices.as_enum())
ACLFamilyEnum = strawberry.enum(ACLFamilyChoices.as_enum())
ACLTypeEnum = strawberry.enum(ACLTypeChoices.as_enum())

#
# Access List Assignments
#

ACLAssignmentDirectionEnum = strawberry.enum(ACLAssignmentDirectionChoices.as_enum())

#
# Access List Rules
#

ACLProtocolEnum = strawberry.enum(ACLProtocolChoices.as_enum())
ACLRuleActionEnum = strawberry.enum(ACLRuleActionChoices.as_enum())

#
# Address Groups
#

ACLAddressFamilyEnum = strawberry.enum(ACLAddressFamilyChoices.as_enum())
