from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['company', 'first_name', 'last_name', 'email', 'phone', 'position', 'avatar', 'notes']
        widgets = {
            'company': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': '+1 (555) 000-0000'}),
            'position': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Position'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Notes...'}),
        }
