from django.contrib import admin

from django.contrib import admin
from .models import StringRecord

@admin.register(StringRecord)
class StringRecordAdmin(admin.ModelAdmin):
    list_display = ('value', 'length', 'is_palindrome', 'word_count', 'created_at')
    search_fields = ('value',)
    list_filter = ('is_palindrome', 'word_count', 'created_at')

