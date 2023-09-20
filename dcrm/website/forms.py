from django.forms import ModelForm
from django import forms
from website.models import TODO


class TODOForm(ModelForm):
    class Meta:
        model = TODO
        fields = ['title', 'status', 'priority']


class EditTaskForm(forms.ModelForm):
    class Meta:
        model = TODO
        fields = ['title', 'priority']
