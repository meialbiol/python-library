import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
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
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
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

            # Create a BookInstance object for test_user1
            return_date = datetime.date.today() + datetime.timedelta(days=5)
            self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
                                                                  due_back=return_date, borrower=test_user1, status='o')

            # Create a BookInstance object for test_user2
            return_date = datetime.date.today() + datetime.timedelta(days=5)
            self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
                                                                  due_back=return_date, borrower=test_user2, status='o')

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
        self.assertEqual(len(resp.context['bookinstance_list']), 10)

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

    def test_redirect_if_not_logged_in_librarian(self):
        resp = self.client.get(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser2')[0])
        resp = self.client.get(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk, }))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(resp.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser2')[0])
        resp = self.client.get(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(resp.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser2')[0])
        resp = self.client.get(reverse('library:renew-book-librarian', kwargs={'pk': 12500, }))
        self.assertEqual(resp.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser2')[0])
        resp = self.client.get(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'library/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser2')[0])
        resp = self.client.get(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser2')[0])
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        resp = self.client.post(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': valid_date_in_future})
        self.assertRedirects(resp, reverse('library:loaned_books'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser2')[0])
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': date_in_past})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.force_login(User.objects.get_or_create(username='testuser2')[0])
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        resp = self.client.post(reverse('library:renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': invalid_date_in_future})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')

