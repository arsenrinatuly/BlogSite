from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Напишите немного о себе..."}),
        label="О себе"
    )
    avatar = forms.ImageField(required=False, label="Аватар")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "bio", "avatar"]

    def save(self, commit=True):
        user = super().save(commit)
        # обновляем профиль
        profile, created = Profile.objects.get_or_create(user=user)
        profile.bio = self.cleaned_data.get("bio")
        if self.cleaned_data.get("avatar"):
            profile.avatar = self.cleaned_data.get("avatar")
        if commit:
            profile.save()
        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar"]