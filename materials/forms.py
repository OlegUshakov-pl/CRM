from django import forms
from .models import Category, Material


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Category name'}),
        }


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'category', 'project', 'quantity', 'unit', 'unit_price', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Material name'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'project': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': '1'}),
            'unit': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'unit_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': '0.00'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Notes...'}),
        }
