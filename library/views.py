import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from library.forms import BookForm
from library.models import Book
from library.models import BookInstance
from library.models import Author
from .forms import RenewBookForm


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5
    context_object_name = 'my_book_list'


class BookDetailView(generic.DetailView):
    model = Book
    context_object_name = 'book'


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5
    context_object_name = 'author_list'


class AuthorDetailView(generic.DetailView):
    model = Author
    context_object_name = 'author'


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'library/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'library/bookinstance_list.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death':'05/01/2018',}
    success_url = reverse_lazy('library:author_list')


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    success_url = reverse_lazy('library:author_list')


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('library:author_list')


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.all().count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(request, 'library/index.html', context={'num_books': num_books,
                                                          'num_instances': num_instances,
                                                          'num_instances_available': num_instances_available,
                                                          'num_authors': num_authors,
                                                          'num_visits': num_visits})


def book_list(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'library/book_list.html', context)


@login_required
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


@login_required
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


@permission_required('library.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            return HttpResponseRedirect(reverse('library:loaned_books'))

    else:

        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    return render(request, 'library/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})
