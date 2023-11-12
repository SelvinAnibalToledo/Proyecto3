from .models import Collection
from django import forms
from django.forms import ModelForm


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = (
            "name",
            "description"
        )