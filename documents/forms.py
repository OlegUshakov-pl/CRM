from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['number', 'file', 'file_type']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Document number',
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors file:mr-3 file:py-1.5 file:px-3 file:border-0 file:bg-gray-100 file:text-sm file:font-medium hover:file:bg-gray-200',
            }),
            'file_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
        }
