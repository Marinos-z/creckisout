from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "checkout/",
        include(("checkout.urls", "checkout"), namespace="checkout"),
    ),
    # Leva visitantes diretamente ao fluxo principal de checkout.
    path("", RedirectView.as_view(pattern_name="checkout:checkout", permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
