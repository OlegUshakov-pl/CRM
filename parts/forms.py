from django import forms
from .models import Category, Part


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


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['number', 'category', 'project', 'size', 'rev', 'created', 'updated']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Part / Drawing number',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'project': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'size': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Size',
            }),
            'rev': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Revision',
            }),
            'created': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'updated': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
        }


class CommonPartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['number', 'category', 'size', 'rev', 'created', 'updated']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Part / Drawing number',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'size': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Size',
            }),
            'rev': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Revision',
            }),
            'created': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'updated': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
        }
