from django.urls import path
from .views import (
    StringListCreateView,
    StringDetailView,
    NaturalLanguageFilterView,
    string_form_view
)

urlpatterns = [
    # 1️⃣ POST /api/strings → create a new string
    # 3️⃣ GET /api/strings  → list all strings
    path("strings", StringListCreateView.as_view(), name="strings_list_create"),

    # 4️⃣ GET /api/strings/filter-by-natural-language → filter strings via natural language query
    path(
        "strings/filter-by-natural-language",
        NaturalLanguageFilterView.as_view(),
        name="strings_filter_by_natural_language"
    ),

    # 5️⃣ GET or DELETE /api/strings/<string_value> → retrieve or delete a specific string
    path("strings/<str:string_value>", StringDetailView.as_view(), name="strings_detail"),

    # Optional HTML form view
    path('string-form/', string_form_view, name='string_form'),
]
