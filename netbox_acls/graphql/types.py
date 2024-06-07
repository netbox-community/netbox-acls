"""
Define the object types and queries availble via the graphql api.
"""

import strawberry
import strawberry_django


from typing import Annotated, List
from .filters import *
from .. import models
from netbox.graphql.types import OrganizationalObjectType

@strawberry_django.type(
    models.AccessList,
    fields='__all__',
    filters=AccessListFilter
)

class AccessListType(OrganizationalObjectType):
    """
    Defines the object type for the django model AccessList.
    """

    class Meta:
        """
        Associates the filterset, fields, and model for the django model AccessList.
        """
        @strawberry_django.field
        def accesslists(self) -> List[Annotated["AccessList", strawberry.lazy('accesslists.graphql.types')]]:
            return self.accesslists.all()
        
@strawberry_django.type(
    models.ACLInterfaceAssignment,
    fields='__all__',
    filters=ACLInterfaceAssignmentFilter
)
class ACLInterfaceAssignmentType(OrganizationalObjectType):
    """
    Defines the object type for the django model AccessList.
    """
    access_list: Annotated["AccessListType", strawberry.lazy("netbox_acls.graphql.types")]
    
    class Meta:
        """
        Associates the filterset, fields, and model for the django model ACLInterfaceAssignment.
        """
        @strawberry_django.field
        def aclinterfaceassignments(self) -> List[Annotated["ACLInterfaceAssignment", strawberry.lazy('aclinterfaceassignments.graphql.types')]]:
            return self.aclinterfaceassignments.all()

@strawberry_django.type(
    models.ACLExtendedRule,
    fields='__all__',
    filters=ACLExtendedRuleFilter
)

class ACLExtendedRuleType(OrganizationalObjectType):
    """
    Defines the object type for the django model ACLExtendedRule.
    """
    source_ports: List[int]
    destination_ports: List[int]
    access_list: Annotated["AccessListType", strawberry.lazy("netbox_acls.graphql.types")]
    destination_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")]
    source_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")]

    class Meta:
        """
        Associates the filterset, fields, and model for the django model ACLExtendedRule.
        """
        @strawberry_django.field
        def aclextendedrules(self) -> List[Annotated["ACLExtendedRule", strawberry.lazy('aclextendedrule.graphql.types')]]:
            return self.aclextendedrules.all()


@strawberry_django.type(
    models.ACLStandardRule,
    fields='__all__',
    filters=ACLStandardRuleFilter
)

class ACLStandardRuleType(OrganizationalObjectType):
    """
    Defines the object type for the django model ACLStandardRule.
    """
    access_list: Annotated["AccessListType", strawberry.lazy("netbox_acls.graphql.types")]
    source_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")]

    class Meta:
        """
        Associates the filterset, fields, and model for the django model ACLExtendedRule.
        """
        @strawberry_django.field
        def aclstandardrules(self) -> List[Annotated["ACLStandardRule", strawberry.lazy('aclstandardrule.graphql.types')]]:
            return self.aclstandardrules.all()

