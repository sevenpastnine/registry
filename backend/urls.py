from debug_toolbar.toolbar import debug_toolbar_urls

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from decorator_include import decorator_include

import backend.registry.urls
import backend.registry.media
import backend.registry.consumers
from backend.auth import site_member_required, CustomPasswordResetView

admin.site.site_title = "Registry Administration"
admin.site.site_header = "Registry Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('backend.registry.api.urls')),
    path('media/<path:path>', backend.registry.media.check_access),
    path('', decorator_include([login_required, site_member_required], (backend.registry.urls, 'registry'), namespace='registry')),  # type: ignore
] + debug_toolbar_urls()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

websocket_urlpatterns = [
    path('ws/registry/study-design-maps/<str:study_design_id>', backend.registry.consumers.YjsConsumer.as_asgi()),
]
