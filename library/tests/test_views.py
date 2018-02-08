import datetime

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from library.models import Author, BookInstance, Book


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


class LoanedBookInstancesByUSerListViewTest(TestCase):

    def setUp(self):
        # create users
        test_user1 = User.objects.create(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create(username='testuser2', password='12345')
        test_user2.save()

        # create book
        test_author = Author.objects.create(first_name='John', last_name='Snow')
        test_book = Book.objects.create(title='Book Title', description='The description', isbn='123456789',
                                        author=test_author)

        # create 30 BookInstance
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'

            BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2006', due_back=return_date,
                                        borrower=the_borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('library:my_borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalogue/mybooks/')

    def test_logged_in_uses_correct_template(self):

        login = self.client.force_login(User.objects.get_or_create(username='testuser1')[0])
        resp = self.client.get(reverse('library:my_borrowed'))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'library/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser1')[0])
        resp = self.client.get(reverse('library:my_borrowed'))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        self.assertFalse('book_instance_list' in resp.context)
        self.assertEqual(len(resp.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # Check that now we have borrowed books in the list
        resp = self.client.get(reverse('library:my_borrowed'))
        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):

        # Change all books to be on loan
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.force_login(User.objects.get_or_create(username='testuser1')[0])
        resp = self.client.get(reverse('library:my_borrowed'))
        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(resp.context['bookinstance_list']), 10)

        last_date = 0
        for copy in resp.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)
