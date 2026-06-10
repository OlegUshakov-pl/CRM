from django import forms
from .models import Contact
from projects.models import Project


class ContactForm(forms.ModelForm):
    projects = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
        label='Project'
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['projects'].queryset = Project.objects.filter(is_active=True)
        order = ['company', 'first_name', 'last_name', 'email', 'phone', 'position', 'projects', 'avatar', 'notes']
        self.fields = {f: self.fields[f] for f in order if f in self.fields}
        if self.instance.pk:
            first_project = self.instance.projects.filter(is_active=True).first()
            if first_project:
                self.fields['projects'].initial = first_project.pk
