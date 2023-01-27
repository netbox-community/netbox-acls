"""
Constants for forms
"""
from django.utils.safestring import mark_safe

# Sets a standard mark_safe help_text value to be used by the various classes
HELP_TEXT_ACL_RULE_LOGIC = mark_safe(
    "<b>*Note:</b> CANNOT be set if action is set to remark.",
)
# Sets a standard help_text value to be used by the various classes for acl action
HELP_TEXT_ACL_ACTION = "Action the rule will take (remark, deny, or allow)."
# Sets a standard help_text value to be used by the various classes for acl index
HELP_TEXT_ACL_RULE_INDEX = (
    "Determines the order of the rule in the ACL processing. AKA Sequence Number."
)

# Sets a standard error message for ACL rules with an action of remark, but no remark set.
ERROR_MESSAGE_NO_REMARK = "Action is set to remark, you MUST add a remark."
# Sets a standard error message for ACL rules with an action of remark, but no source_prefix is set.
ERROR_MESSAGE_ACTION_REMARK_SOURCE_PREFIX_SET = (
    "Action is set to remark, Source Prefix CANNOT be set."
)
# Sets a standard error message for ACL rules with an action not set to remark, but no remark is set.
ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK = (
    "CANNOT set remark unless action is set to remark."
)
