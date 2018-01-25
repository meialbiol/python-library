from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.


class Book(models.Model):
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=250)
    description = models.TextField(null=True)
    isbn = models.CharField(max_length=13, null=True)
    year = models.IntegerField(null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.title


class BookInstance(models.Model):
    """
    Represents the stat of a book
    """

    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200,null=True, blank=True)
    due_back= models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved')
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, default='m', help_text='Available Book')

    class Meta:
        ordering = ["due_back"]

    def __str__(self):
        return '{0} ({1})'.format(self.id, self.book.title)


class Author(models.Model):
    """
    Represents the Author Model
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """
        Returns the absolute url to an author
        :return:
        """

        return reverse('author_detail', args=[str(self.id)])

    def __str__(self):

        return '{0}, {1}'.format(self.last_name, self.first_name)