from django import forms
from django.contrib.auth.forms import AuthenticationForm


class TaiKhoanLoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'field-input',
        'placeholder': 'Tên đăng nhập'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'field-input',
        'placeholder': 'Mật khẩu'
    }))

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username or not password:
            raise forms.ValidationError("Vui lòng nhập đầy đủ thông tin.")

        return cleaned_data