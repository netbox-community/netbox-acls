"""Field mixins shared by the extensions contributed to NetBox's GraphQL types."""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from utilities.querysets import RestrictedPrefetch

from ..models import ACLAssignment, ACLExtendedRule, ACLStandardRule

if TYPE_CHECKING:
    from ..graphql.types import ACLAssignmentType, ACLExtendedRuleType, ACLStandardRuleType

__all__ = (
    "ACLAssignmentReferences",
    "ACLRuleReferences",
)


def _restricted(accessor, model):
    """Build a prefetch narrowed to the objects the requesting user may view.

    Core re-applies restrict() when resolving, so this narrows what gets cached
    rather than being the thing that enforces the permission.
    """

    def prefetch(info):
        return RestrictedPrefetch(accessor, info.context.request.user, "view", queryset=model.objects.all())

    return prefetch


@strawberry.type
class ACLAssignmentReferences:
    """The ACL assignments attached to a host or interface object."""

    @strawberry_django.field(prefetch_related=_restricted("aclassignments", ACLAssignment))
    def acl_assignments(
        self,
    ) -> list[Annotated["ACLAssignmentType", strawberry.lazy("netbox_acls.graphql.types")]]:
        """Return the ACL assignments attached to this object."""
        return self.aclassignments.all()


@strawberry.type
class ACLRuleReferences:
    """The ACL rules referencing an IPAM object as their source or destination."""

    @strawberry_django.field(
        prefetch_related=_restricted("accesslist_standard_rule_sources", ACLStandardRule),
    )
    def acl_standard_rule_sources(
        self,
    ) -> list[Annotated["ACLStandardRuleType", strawberry.lazy("netbox_acls.graphql.types")]]:
        """Return the Standard ACL rules using this object as their source."""
        return self.accesslist_standard_rule_sources.all()

    @strawberry_django.field(
        prefetch_related=_restricted("accesslist_extended_rule_sources", ACLExtendedRule),
    )
    def acl_extended_rule_sources(
        self,
    ) -> list[Annotated["ACLExtendedRuleType", strawberry.lazy("netbox_acls.graphql.types")]]:
        """Return the Extended ACL rules using this object as their source."""
        return self.accesslist_extended_rule_sources.all()

    @strawberry_django.field(
        prefetch_related=_restricted("accesslist_extended_rule_destinations", ACLExtendedRule),
    )
    def acl_extended_rule_destinations(
        self,
    ) -> list[Annotated["ACLExtendedRuleType", strawberry.lazy("netbox_acls.graphql.types")]]:
        """Return the Extended ACL rules using this object as their destination."""
        return self.accesslist_extended_rule_destinations.all()
