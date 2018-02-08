from django.test import TestCase

from library.models import Author

class AuthorModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object = '%s, %s' % (author.last_name, author.first_name)
        self.assertEquals(expected_object, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)

        self.assertEquals(author.get_absolute_url(), '/catalogue/author/1/')