from django.urls import path

from netbox.views.generic import ObjectChangeLogView
from . import models, views


urlpatterns = (

    # Access-Lists
    path('access-lists/', views.AccessListListView.as_view(), name='accesslist_list'),
    path('access-lists/add/', views.AccessListEditView.as_view(), name='accesslist_add'),
    path('access-lists/<int:pk>/', views.AccessListView.as_view(), name='accesslist'),
    path('access-lists/<int:pk>/edit/', views.AccessListEditView.as_view(), name='accesslist_edit'),
    path('access-lists/<int:pk>/delete/', views.AccessListDeleteView.as_view(), name='accesslist_delete'),
    path('access-lists/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='accesslist_changelog', kwargs={
        'model': models.AccessList
    }),

    # Standard Access-List rules
    path('standard-rules/', views.ACLStandardRuleListView.as_view(), name='aclstandardrule_list'),
    path('standard-rules/add/', views.ACLStandardRuleEditView.as_view(), name='aclstandardrule_add'),
    path('standard-rules/<int:pk>/', views.ACLStandardRuleView.as_view(), name='aclstandardrule'),
    path('standard-rules/<int:pk>/edit/', views.ACLStandardRuleEditView.as_view(), name='aclstandardrule_edit'),
    path('standard-rules/<int:pk>/delete/', views.ACLStandardRuleDeleteView.as_view(), name='aclstandardrule_delete'),
    path('standard-rules/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='aclstandardrule_changelog', kwargs={
        'model': models.ACLStandardRule
    }),

    # Extended Access-List rules
    path('extended-rules/', views.ACLExtendedRuleListView.as_view(), name='aclextendedrule_list'),
    path('extended-rules/add/', views.ACLExtendedRuleEditView.as_view(), name='aclextendedrule_add'),
    path('extended-rules/<int:pk>/', views.ACLExtendedRuleView.as_view(), name='aclextendedrule'),
    path('extended-rules/<int:pk>/edit/', views.ACLExtendedRuleEditView.as_view(), name='aclextendedrule_edit'),
    path('extended-rules/<int:pk>/delete/', views.ACLExtendedRuleDeleteView.as_view(), name='aclextendedrule_delete'),
    path('extended-rules/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='aclextendedrule_changelog', kwargs={
        'model': models.ACLExtendedRule
    }),

)
