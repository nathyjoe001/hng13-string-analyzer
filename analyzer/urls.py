from django.urls import path
from .views import (
    StringListCreateView,
    StringDetailView,
    NaturalLanguageFilterView,
)

urlpatterns = [
    # GET / POST /strings
    path("strings", StringListCreateView.as_view(), name="strings_list_create"),
    
    # GET / DELETE /strings/{string_value}
    path("strings/<str:string_value>", StringDetailView.as_view(), name="strings_detail"),
    
    # GET /strings/filter-by-natural-language
    path("strings/filter-by-natural-language", NaturalLanguageFilterView.as_view(), name="strings_filter_by_natural_language"),
]