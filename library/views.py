from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic

# Create your views here.
from django.urls import reverse

from library.forms import BookForm
from library.models import Book
from library.models import BookInstance
from library.models import Author


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'my_book_list'

class BookDetailView(generic.DetailView):
    model = Book
    context_object_name='book'

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.all().count()

    return render(request, 'library/index.html', context={'num_books': num_books, 'num_instances': num_instances, 'num_instances_available': num_instances_available, 'num_authors': num_authors})

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
            book = form.save()
            book_instance = BookInstance(
                status='a',
                book_id=book.id
            )
            book_instance.save()
            return HttpResponseRedirect(reverse('library:book_list'))

    context = {'form': form}
    return render(request, 'library/new_book.html', context)


def show(request, book_id):
    book = Book.objects.get(id=book_id)
    context = {'book': book}

    return render(request, 'library/book_detail.html', context)


def edit(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.method != 'POST':
        form = BookForm(instance=book)
    else:
        form = BookForm(instance=book, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('library:show_book', args=[book.id]))

    context = {'book': book, 'form': form}
    return render(request, 'library/edit.html', context)