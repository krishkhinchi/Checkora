from django import forms
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

from .models import UserProfile
from django.core.exceptions import ValidationError
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar', False)
        if avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5MB ).")
            
            try:
                img = Image.open(avatar)
                if img.mode in ("RGBA", "P"):
                    img = img.convert('RGB')
                img.thumbnail((256, 256), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                
                avatar = InMemoryUploadedFile(
                    output, 'ImageField', f"{avatar.name.split('.')[0]}.jpg",
                    'image/jpeg', sys.getsizeof(output), None
                )
            except Exception as e:
                raise ValidationError("Invalid image format.")
        return avatar
