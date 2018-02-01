from django import forms
from django.core.exceptions import ValidationError

from .models import Book

import datetime


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['author', 'title', 'description', 'isbn', 'year']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'class': 'materialize-textarea'}),
            'year': forms.NumberInput(attrs={'min': '0', 'max': '9999', 'step': '1'})
        }


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Seleccione una fecha entra hoy y 4 semanas (por defecto 3 semanas)")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Chek date is not in the past
        if data < datetime.date.today():
            raise ValidationError(('Invalida date - renewal in past'))

        # Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(('Invalida date - renewal more than 4 weeks ahead'))

        return data