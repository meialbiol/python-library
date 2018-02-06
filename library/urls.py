from django.conf.urls import url

from . import views

urlpatterns = [
    #homepage
    url(r'^$', views.index, name='index'),
    # url(r'^catalogue/books/$', views.book_list, name='book_list'),
    url(r'^catalogue/books/$', views.BookListView.as_view(), name='book_list'),
    url(r'^catalogue/book/(?P<pk>\d+)/$', views.BookDetailView.as_view(), name='show_book'),
    url(r'^catalogue/book/(?P<pk>\d+)/renew/$', views.renew_book_librarian, name='renew-book-librarian'),
    # url('catalogue/book/<int:pk>', views.BookDetailView.as_view(), name='book_detail'),
    url(r'^new_book/$', views.new_book, name='new_book'),
    url(r'^book/edit/(?P<pk>\d+)/$', views.edit, name='edit_book'),

    url(r'^catalogue/author/$', views.AuthorListView.as_view(), name='author_list'),
    url(r'^catalogue/author/(?P<pk>\d+)/$', views.AuthorDetailView.as_view(), name='author_detail'),
    url(r'^catalogue/author/create/$', views.AuthorCreate.as_view(), name='author_create'),
    url(r'^catalogue/(?P<pk>\d+)/update/$', views.AuthorUpdate.as_view(), name='author_update'),
    url(r'^catalogue/(?P<pk>\d+)/delete/$', views.AuthorDelete.as_view(), name='author_delete'),
    url(r'^catalogue/mybooks/$', views.LoanedBooksByUserListView.as_view(), name='my_borrowed'),
    url(r'^catalogue/loaned/$', views.LoanedBooksListView.as_view(), name='loaned_books')
]

