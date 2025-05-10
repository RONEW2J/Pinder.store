from django import forms
from .models import Profile, Interest, Photo
from django.contrib.gis.forms import PointField # For location

class ProfileEditForm(forms.ModelForm):
    # You might want to use a widget that's easier for users to input coordinates,
    # or handle location updates differently (e.g., via JavaScript and a map API).
    # For now, PointField will render as a text input expecting WKT or similar.
    location = PointField(
        required=False,
        help_text="Enter as 'POINT(longitude latitude)', e.g., POINT(-0.1278 51.5074). You can find your coordinates using an online map tool."
    )
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us a bit about yourself...'}), required=False)

    class Meta:
        model = Profile
        fields = ['age', 'bio', 'location', 'interests']

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'caption'] # Add 'is_profile_picture' if you want to set it on upload
        widgets = {
            'caption': forms.Textarea(attrs={'rows': 3}),
        }