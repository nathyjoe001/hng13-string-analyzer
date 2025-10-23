
import uuid
import hashlib
from django.db import models
from django.utils import timezone

# Create your models here.
class StringRecord(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
        )
    value = models.TextField(unique=True)
    sha256_hash = models.CharField(max_length=64, unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    def save (self, *arg, **kwarg):
        self.sha256_hash = hashlib.sha256(
            self.value.encode('utf-8')).hexdigest()
        
        super().save(*arg, **kwarg)

        def __str__(self):
            return self.value
        
