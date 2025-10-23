from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="String Analyzer API",
        default_version='v1',
        description="Analyze strings and view results",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('analyzer.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]
