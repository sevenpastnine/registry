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
from backend.auth import (
    site_member_required,
    PasswordResetView,
    activation_request,
    activation_done,
    activation_complete,
    activation_confirm,
)

admin.site.site_title = "Registry Administration"
admin.site.site_header = "Registry Administration"

urlpatterns = [
    path('admin/', admin.site.urls),

    # User authentication and account management
    path('accounts/password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('accounts/activate/', activation_request, name='activation'),
    path('accounts/activate/done/', activation_done, name='activation_done'),
    path('accounts/activate/complete/', activation_complete, name='activation_complete'),
    path('accounts/activate/<str:token>/', activation_confirm, name='activation_confirm'),
    path('accounts/', include('django.contrib.auth.urls')),  # includes login, logout, password change, etc.

    # API endpoints
    path('api/', include('backend.registry.api.urls')),

    # Protected media access
    path('media/<path:path>', backend.registry.media.check_access),

    # Registry URLs
    path('', decorator_include([login_required, site_member_required], (backend.registry.urls, 'registry'), namespace='registry')),  # type: ignore
] + debug_toolbar_urls()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

websocket_urlpatterns = [
    path('ws/registry/study-design-maps/<str:study_design_id>', backend.registry.consumers.YjsConsumer.as_asgi()),  # type: ignore
]
