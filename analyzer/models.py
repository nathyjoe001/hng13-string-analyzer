import hashlib
from django.db import models
from django.utils import timezone

class StringRecord(models.Model):
    id = models.CharField(primary_key=True, max_length=64, editable=False)  # use hash as ID
    value = models.TextField(unique=True)
    sha256_hash = models.CharField(max_length=64, unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Compute SHA-256 hash
        self.sha256_hash = hashlib.sha256(self.value.encode('utf-8')).hexdigest()
        # Set hash as ID
        self.id = self.sha256_hash
        super().save(*args, **kwargs)

    def __str__(self):
        return self.value
