from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class StyledUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "style": "width:100%; padding:0.7rem 0.9rem; border:1.5px solid #e2e8f0; border-radius:8px; font-size:0.95rem; outline:none;"
            })
