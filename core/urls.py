from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace="accounts")),
    path('students/', include('apps.students.urls', namespace="students")),
    path('elections/', include('apps.elections.urls', namespace="elections")),
]

admin.site.site_header = f"{settings.APPLICATION_NAME} Admin"
admin.site.site_title = f"{settings.APPLICATION_ALIAS} Admin"
