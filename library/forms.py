from django import forms
from .models import LibraryItem, Category, Tag


class LibraryItemForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            'placeholder': 'Enter tags separated by commas',
            'list': 'existing-tags',
        }),
        label='Tags'
    )

    class Meta:
        model = LibraryItem
        fields = ['title', 'description', 'content', 'category', 'file', 'is_favorite']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Document title',
            }),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Short description...',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['category'].required = False
        self.fields['content'].required = False
        self.fields['content'].widget = forms.HiddenInput()
        self.fields['description'].required = False
        self.fields['file'].required = False

        if self.instance.pk:
            tags_str = ', '.join(self.instance.tags.all().values_list('name', flat=True))
            self.fields['tags_input'].initial = tags_str

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self._save_tags(instance)
        return instance

    def _save_tags(self, instance):
        tags_str = self.cleaned_data.get('tags_input', '')
        if tags_str:
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            tags = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                tags.append(tag)
            instance.tags.set(tags)
        else:
            instance.tags.clear()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color', 'icon', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'Category name',
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'e.g. #8B5CF6',
            }),
            'icon': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
                'placeholder': 'lucide icon name',
            }),
            'parent': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-[#e8e8e8] text-[14px] outline-none focus:border-violet-300 transition-colors',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.filter(is_active=True)
        self.fields['parent'].required = False
        self.fields['color'].required = False
        self.fields['icon'].required = False
