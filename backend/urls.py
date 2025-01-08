from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from decorator_include import decorator_include

import backend.registry.urls
import backend.registry.media
from backend.auth import site_member_required

admin.site.site_title = "Registry Administration"
admin.site.site_header = "Registry Administration"

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('backend.registry.api.urls')),
    path('media/<path:path>', backend.registry.media.check_access),
    path('', decorator_include([login_required, site_member_required], (backend.registry.urls, 'registry'), namespace='registry')),  # type: ignore
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
