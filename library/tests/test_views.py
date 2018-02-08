from django.test import TestCase

from library.models import Author
from django.urls import reverse


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name='Surname %s' % author_num, )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalogue/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('library:author_list'))
        self.assertEqual(resp.status_code, 200)

    def test_view_usees_correct_template(self):
        resp = self.client.get(reverse('library:author_list'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'library/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('library:author_list'))
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list']) == 5)
