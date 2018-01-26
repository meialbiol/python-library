from django.contrib import admin
from .models import Book, BookInstance, Author


class BookInline(admin.TabularInline):
    model = Book

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]


# Register your models here.
# admin / Actualmola05

# admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Author, AuthorAdmin)

class BookInstanceInline(admin.TabularInline):
    model = BookInstance

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    inlines = [BookInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book','status','borrower', 'due_back')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
           'fields': ('book', 'imprint')
        }),
        ('Availability', {
           'fields': ('status', 'due_back', 'borrower')
        }),
    )
