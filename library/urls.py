from django.conf.urls import url

from . import views

urlpatterns = [
    #homepage
    url(r'^$', views.index, name='index'),
    url(r'^book-list/$', views.book_list, name='book_list'),
    url(r'^new_book/$', views.new_book, name='new_book'),
]

