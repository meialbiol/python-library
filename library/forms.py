from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['author', 'title', 'description', 'isbn', 'year']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'class': 'materialize-textarea'}),
            'year': forms.NumberInput(attrs={'min': '0', 'max': '9999', 'step': '1'})
            }

