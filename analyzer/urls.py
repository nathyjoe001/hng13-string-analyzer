from django.urls import path
from .views import (
    AnalyzeStringView,
    StringDetailView,
    StringListView,
    NaturalLanguageFilterView,
)

urlpatterns = [
    # 1️⃣ POST /api/strings  → create & analyze a new string
    path("strings", AnalyzeStringView.as_view(), name="strings_create"),

    # 2️⃣ GET /api/strings/filter-by-natural-language  → natural language filtering
    path("strings/filter-by-natural-language", NaturalLanguageFilterView.as_view(), name="strings_filter_by_natural_language"),

    # 3️⃣ GET /api/strings  → list all strings with filters
    path("strings/all", StringListView.as_view(), name="strings_list"),  # renamed endpoint to avoid conflict

    # 4️⃣ GET or DELETE /api/strings/<string_value> → retrieve or delete specific string
    path("strings/<str:string_value>", StringDetailView.as_view(), name="strings_detail"),
]
