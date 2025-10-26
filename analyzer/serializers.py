# analyzer/serializers.py
from rest_framework import serializers
from .models import StringRecord

class PropertiesSerializer(serializers.Serializer):
    length = serializers.IntegerField()
    is_palindrome = serializers.BooleanField()
    unique_characters = serializers.IntegerField()
    word_count = serializers.IntegerField()
    sha256_hash = serializers.CharField()
    character_frequency_map = serializers.DictField(child=serializers.IntegerField())

class StringRecordSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = StringRecord
        fields = ("id", "value", "properties", "created_at")

    def get_properties(self, obj):
        return {
            "length": obj.length,
            "is_palindrome": obj.is_palindrome,
            "unique_characters": obj.unique_characters,
            "word_count": obj.word_count,
            "sha256_hash": obj.sha256_hash,
            "character_frequency_map": obj.character_frequency_map,
        }
