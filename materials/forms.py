from django import forms
from .models import Category, Material, MaterialFile
from projects.models import Project


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Category name'}),
        }


class MaterialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(is_active=True)

    class Meta:
        model = Material
        fields = ['name', 'number', 'category', 'project', 'quantity', 'unit', 'unit_price', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Material name'}),
            'number': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Material number'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'project': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': '1'}),
            'unit': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'unit_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': '0.00'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Notes...'}),
        }


class CommonMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'category', 'quantity', 'unit', 'unit_price', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Material name'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': '1'}),
            'unit': forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors'}),
            'unit_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': '0.00'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors', 'placeholder': 'Notes...'}),
        }


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


ALLOWED_MATERIAL_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.xls', '.xlsx', '.txt', '.docx', '.ods'}


class MaterialFileForm(forms.ModelForm):
    file = MultipleFileField(
        label='Files', required=True,
        widget=MultipleFileInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors file:mr-3 file:py-1.5 file:px-3 file:border-0 file:bg-gray-100 file:text-sm file:font-medium hover:file:bg-gray-200',
            'accept': '.pdf,.jpg,.jpeg,.png,.xls,.xlsx,.txt,.docx,.ods',
        }),
    )

    class Meta:
        model = MaterialFile
        fields = ['file']
