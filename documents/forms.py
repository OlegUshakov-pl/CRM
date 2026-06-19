from django import forms
from django.db.models import Q
from projects.models import Project
from .models import Document, Category


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        if result == [None]:
            return None
        return result


class DocumentForm(forms.ModelForm):
    file = MultipleFileField(
        label='File', required=False,
        widget=MultipleFileInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors file:mr-3 file:py-1.5 file:px-3 file:border-0 file:bg-gray-100 file:text-sm file:font-medium hover:file:bg-gray-200',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].required = False
        self.fields['project'].queryset = Project.objects.filter(is_active=True)
        self.fields['category'].queryset = Category.objects.all()

    class Meta:
        model = Document
        fields = ['project', 'number', 'file', 'category']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Document number',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
        }


class CommonDocumentForm(forms.ModelForm):
    file = MultipleFileField(
        label='File', required=False,
        widget=MultipleFileInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors file:mr-3 file:py-1.5 file:px-3 file:border-0 file:bg-gray-100 file:text-sm file:font-medium hover:file:bg-gray-200',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].required = False
        self.fields['project'].queryset = Project.objects.filter(is_active=True)
        self.fields['category'].queryset = Category.objects.all()

    class Meta:
        model = Document
        fields = ['project', 'number', 'file', 'category']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Document number',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Category name',
            }),
        }
