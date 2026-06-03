from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.template import loader
from django.core.mail import EmailMessage


def get_initials(self):
    if self.first_name and self.last_name:
        return f"{self.first_name[0]}{self.last_name[0]}".upper()
    return self.username[:2].upper()


User.add_to_class('get_initials', get_initials)


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none', 'placeholder': 'Password'}))


class NoWrapEmail(EmailMessage):
    """EmailMessage that prevents quoted-printable line wrapping."""
    def message(self):
        msg = super().message()
        for part in msg.walk():
            if part.get_content_maintype() == 'text':
                payload = part.get_payload(decode=True)
                if payload is not None:
                    charset = part.get_content_charset() or 'utf-8'
                    part.set_payload(payload.decode(charset), charset)
                    part.replace_header('Content-Transfer-Encoding', '7bit')
        return msg


class PasswordResetForm(BasePasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'style': 'width: 100%; font-size: 16px; border: 1px solid #ccc; padding: 10px 12px; outline: none; box-sizing: border-box;',
        })

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        msg = NoWrapEmail(subject, body, from_email, [to_email])
        msg.send()


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
