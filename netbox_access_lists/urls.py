from django.urls import path

from netbox.views.generic import ObjectChangeLogView
from . import models, views


urlpatterns = (

    # Access lists
    path('access-lists/', views.AccessListListView.as_view(), name='accesslist_list'),
    path('access-lists/add/', views.AccessListEditView.as_view(), name='accesslist_add'),
    path('access-lists/<int:pk>/', views.AccessListView.as_view(), name='accesslist'),
    path('access-lists/<int:pk>/edit/', views.AccessListEditView.as_view(), name='accesslist_edit'),
    path('access-lists/<int:pk>/delete/', views.AccessListDeleteView.as_view(), name='accesslist_delete'),
    path('access-lists/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='accesslist_changelog', kwargs={
        'model': models.AccessList
    }),

    # Standard Access list rules
    path('standard-rules/', views.AccessListStandardRuleListView.as_view(), name='accessliststandardrule_list'),
    path('standard-rules/add/', views.AccessListStandardRuleEditView.as_view(), name='accessliststandardrule_add'),
    path('standard-rules/<int:pk>/', views.AccessListStandardRuleView.as_view(), name='accessliststandardrule'),
    path('standard-rules/<int:pk>/edit/', views.AccessListStandardRuleEditView.as_view(), name='accessliststandardrule_edit'),
    path('standard-rules/<int:pk>/delete/', views.AccessListStandardRuleDeleteView.as_view(), name='accessliststandardrule_delete'),
    path('standard-rules/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='accessliststandardrule_changelog', kwargs={
        'model': models.AccessListStandardRule
    }),

    # Extended Access list rules
    path('extended-rules/', views.AccessListExtendedRuleListView.as_view(), name='accesslistextendedrule_list'),
    path('extended-rules/add/', views.AccessListExtendedRuleEditView.as_view(), name='accesslistextendedrule_add'),
    path('extended-rules/<int:pk>/', views.AccessListExtendedRuleView.as_view(), name='accesslistextendedrule'),
    path('extended-rules/<int:pk>/edit/', views.AccessListExtendedRuleEditView.as_view(), name='accesslistextendedrule_edit'),
    path('extended-rules/<int:pk>/delete/', views.AccessListExtendedRuleDeleteView.as_view(), name='accesslistextendedrule_delete'),
    path('extended-rules/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='accesslistextendedrule_changelog', kwargs={
        'model': models.AccessListExtendedRule
    }),

)
