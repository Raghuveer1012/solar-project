from django.contrib import admin
from django.urls import path, include

# Customize admin site branding for Kartavya Solar
admin.site.site_header = "Kartavya Solar Admin"
admin.site.site_title = "Kartavya Solar Admin"
admin.site.index_title = "Kartavya Solar Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]
