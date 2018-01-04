from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from library.forms import BookForm
from library.models import Book


def index(request):
    return render(request, 'library/index.html')


def book_list(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'library/book_list.html', context)

def new_book(request):
    if request.method != 'POST':
        form = BookForm()
    else:
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('library:book_list'))

    context = {'form': form}
    return render(request, 'library/new_book.html', context)

def show(request, book_id):
    book = Book.objects.get(id=book_id)
    context = {'book': book}

    return render(request,'library/show.html', context)
