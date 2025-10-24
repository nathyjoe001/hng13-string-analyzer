from django.urls import path
from .views import (
    StringListCreateView,
    StringDetailView,
    NaturalLanguageFilterView,
)

urlpatterns = [
    # 1️⃣ POST /api/strings  → create a string
    # 3️⃣ GET /api/strings   → list strings
    path("strings", StringListCreateView.as_view(), name="strings_list_create"),

    # 4️⃣ GET /api/strings/filter-by-natural-language
    path("strings/filter-by-natural-language", NaturalLanguageFilterView.as_view(),
         name="strings_filter_by_natural_language"),

    # 5️⃣ GET or DELETE /api/strings/<string_value>
    path("strings/<str:string_value>", StringDetailView.as_view(), name="strings_detail"),
]
