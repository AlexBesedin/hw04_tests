from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea,
        label="Введите текст",
        required=True,
        help_text="Текст поста",
    )

    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {"group": "Выберите нужную группу"}
        help_text = {"group": "Группа поста"}
