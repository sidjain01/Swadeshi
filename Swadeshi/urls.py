from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import myapp
import myapp.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', myapp.views.landing_page, name="landing"),
    path('contact/', myapp.views.contact_page, name="landing_contact"),
    path('shop/', include('myapp.urls')),
    path('agent/', include('myapp.agent_urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
