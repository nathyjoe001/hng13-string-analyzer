from django.urls import path
from .views import (
    StringListCreateView,
    StringDetailView,
    NaturalLanguageFilterView,
)

urlpatterns = [
    # 1️⃣ GET / POST → list all strings or create a new analyzed string
    path("strings", StringListCreateView.as_view(), name="strings_list_create"),

    # 2️⃣ GET /api/strings/filter-by-natural-language → natural language filtering
    path("strings/filter-by-natural-language", NaturalLanguageFilterView.as_view(), name="strings_filter_by_natural_language"),

    # 3️⃣ GET / DELETE /api/strings/<string_value> → retrieve or delete specific string
    path("strings/<str:string_value>", StringDetailView.as_view(), name="strings_detail"),
]
