from django.db import models
from django.utils import timezone

# Create your models here.


class Book(models.Model):
    author = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    description = models.TextField(null=True)
    isbn = models.CharField(max_length=13, null=True)
    year = models.IntegerField(null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.title
