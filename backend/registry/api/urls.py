from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'people', views.PersonViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'licenses', views.LicenseViewSet)
router.register(r'person-roles', views.PersonRoleViewSet)
router.register(r'resource-kinds', views.ResourceKindViewSet, basename='resourcekind')
router.register(r'resource-statuses', views.ResourceStatusViewSet)
router.register(r'resources', views.ResourceViewSet)
router.register(r'resource-files', views.ResourceFileViewSet)

urlpatterns = [
    path('docs/', views.docs, name='api_docs'),
    path('', include(router.urls)),
]
