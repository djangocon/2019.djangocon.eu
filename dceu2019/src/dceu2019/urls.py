"""
dceu2019 URL Configuration.

The ``urlpatterns`` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/

Examples:
    Function views
        1. Add an import: from dceu2019.apps.my_app import views
        2. Add a URL to urlpatterns: path("", views.home, name="home")
    Class-based views
        1. Add an import: from dceu2019.apps.other_app.views import Home
        2. Add a URL to urlpatterns: path("", Home.as_view(), name="home")
    Including another URLconf
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns: path("blog/", include("dceu2019.apps.blog.urls"))

"""
from dceu2019.apps.ticketholders.views import IndexView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/", include('loginas.urls')),
    path('orga/', include('pretalx.orga.urls', namespace='orga')),
    path('api/', include('pretalx.api.urls', namespace='api')),
    path('ticketholder/', include('dceu2019.apps.ticketholders.urls', namespace='ticketholder')),
    path('tickets/', include('dceu2019.apps.invoices.urls', namespace='invoices')),
    path('', IndexView.as_view(), name='index'),
    path('', include('pretalx.agenda.urls', namespace='agenda')),
    path('', include('pretalx.cfp.urls', namespace='cfp')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
