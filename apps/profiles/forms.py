from django import forms
from .models import Profile, Interest, Photo, City

class ProfileEditForm(forms.ModelForm):
    # You might want to use a widget that's easier for users to input coordinates,
    # or handle location updates differently (e.g., via JavaScript and a map API).
    # For now, PointField will render as a text input expecting WKT or similar.
    city = forms.ModelChoiceField(
        queryset=City.objects.all().order_by('name'), # Or however you want to order/filter cities
        required=False, # Or True, depending on your model
        label="Your City",
        widget=forms.Select(attrs={'class': 'form-control'}) # Standard select dropdown
    )
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us a bit about yourself...'}), required=False)

    class Meta:
        model = Profile
        fields = ['age', 'bio', 'city', 'interests', 'gender', 'phone_number']

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'caption', 'is_profile_avatar']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
            'is_profile_avatar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }