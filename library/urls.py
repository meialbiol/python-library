from django.conf.urls import url

from . import views

urlpatterns = [
    #homepage
    url(r'^$', views.index, name='index'),
    url(r'^books/$', views.book_list, name='book_list'),
    url(r'^new_book/$', views.new_book, name='new_book'),
    url(r'^book/(?P<book_id>\d+)/$', views.show, name='show_book'),
    url(r'^book/edit/(?P<book_id>\d+)/$', views.edit, name='edit_book'),
]

