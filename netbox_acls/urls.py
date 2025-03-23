"""
Map Views to URLs.
"""

from django.urls import include, path
from utilities.urls import get_model_urls

from . import views  # noqa F401

urlpatterns = (
    # Access Lists
    path(
        "access-lists/",
        include(get_model_urls("netbox_acls", "accesslist", detail=False)),
    ),
    path(
        "access-lists/<int:pk>/",
        include(get_model_urls("netbox_acls", "accesslist")),
    ),
    # Access List Interface Assignments
    path(
        "interface-assignments/",
        include(get_model_urls("netbox_acls", "aclinterfaceassignment", detail=False)),
    ),
    path(
        "interface-assignments/<int:pk>/",
        include(get_model_urls("netbox_acls", "aclinterfaceassignment")),
    ),
    # Standard Access List Rules
    path(
        "standard-rules/",
        include(get_model_urls("netbox_acls", "aclstandardrule", detail=False)),
    ),
    path(
        "standard-rules/<int:pk>/",
        include(get_model_urls("netbox_acls", "aclstandardrule")),
    ),
    # Extended Access List Rules
    path(
        "extended-rules/",
        include(get_model_urls("netbox_acls", "aclextendedrule", detail=False)),
    ),
    path(
        "extended-rules/<int:pk>/",
        include(get_model_urls("netbox_acls", "aclextendedrule")),
    ),
)
