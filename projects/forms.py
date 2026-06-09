from django import forms
from .models import Project
from companies.models import Company


class ProjectForm(forms.ModelForm):
    number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'xxx-xxx-xxx'})
    )

    class Meta:
        model = Project
        fields = ['number', 'name', 'description', 'status', 'company', 'start_date', 'end_date', 'budget', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Project name', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Project description...'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'company': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'budget': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(is_active=True)
