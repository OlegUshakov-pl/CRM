from django import forms
from django.contrib.auth.models import User


def get_initials(self):
    if self.first_name and self.last_name:
        return f"{self.first_name[0]}{self.last_name[0]}".upper()
    return self.username[:2].upper()


User.add_to_class('get_initials', get_initials)


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none', 'placeholder': 'Password'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-[#e8e8e8] text-[13px] outline-none focus:border-violet-300 transition-colors'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-[#e8e8e8] text-[13px] outline-none focus:border-violet-300 transition-colors'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-[#e8e8e8] text-[13px] outline-none focus:border-violet-300 transition-colors'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-[#e8e8e8] text-[13px] outline-none focus:border-violet-300 transition-colors'}),
        }
