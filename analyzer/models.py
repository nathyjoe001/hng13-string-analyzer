# analyzer/models.py
import hashlib
from django.db import models
from django.utils import timezone

class StringRecord(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)  # sha256 hex
    value = models.CharField(max_length=1000, unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    sha256_hash = models.CharField(max_length=64)  # duplicate but explicit
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # compute sha256 and set id if not provided
        import hashlib
        sha = hashlib.sha256(self.value.encode()).hexdigest()
        self.sha256_hash = sha
        if not self.id:
            self.id = sha
        super().save(*args, **kwargs)

    def __str__(self):
        return self.value
