from django.shortcuts import render

# Create your views here.
from library.models import Book


def index(request):
    return render(request, 'library/index.html')


def book_list(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'library/book_list.html', context)
