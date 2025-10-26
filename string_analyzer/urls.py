from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "String Analyzer API is live!"})

schema_view = get_schema_view(
    openapi.Info(
        title="String Analyzer API",
        default_version='v1',
        description="Analyze strings and view results",
    ),
    public=True,
)

urlpatterns = [
    path('', home),  # Root URL
    path('admin/', admin.site.urls),
    path('', include('analyzer.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]
