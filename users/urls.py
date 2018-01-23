from django.conf.urls import url

from . import views

urlpatterns = [
    #users
    url(r'^users/$', views.book_list, name='user_list')
    ]