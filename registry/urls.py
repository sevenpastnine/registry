from django.urls import path

from . import views

app_name = 'registry'


urlpatterns = [
    path('', views.index, name='index'),
    path('people/', views.people, name='people'),
    path('people/<slug:person_id>/', views.person, name='person'),
    path('organisations/', views.organisations, name='organisations'),
    path('organisations/<slug:organisation_id>/', views.organisation, name='organisation'),
    path('groups/', views.groups, name='groups'),
    path('groups/<slug:group_id>/', views.group, name='group'),
    path('licenses/', views.licenses, name='licenses'),
    path('licenses/<slug:license_id>/', views.license, name='license'),
    path('resources/', views.resources, name='resources'),
    path('resources/add/', views.resource_add, name='resource_add'),
    path('resources/<slug:resource_id>/', views.resource, name='resource'),
    path('resources/<slug:resource_id>/edit/', views.resource_edit, name='resource_edit'),
    path('study-designs/', views.study_designs, name='study_designs'),
    path('study-designs/add/', views.study_design_add, name='study_design_add'),
    path('study-designs/<slug:study_design_id>/', views.study_design, name='study_design'),
    path('study-designs/<slug:study_design_id>/edit/', views.study_design_edit, name='study_design_edit'),
]
