from django import forms
from .models import Profile, Interest
from django.contrib.gis.forms import PointField # For location

class ProfileEditForm(forms.ModelForm):
    # You might want to use a widget that's easier for users to input coordinates,
    # or handle location updates differently (e.g., via JavaScript and a map API).
    # For now, PointField will render as a text input expecting WKT or similar.
    location = PointField(required=False)
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Profile
        fields = ['age', 'location', 'interests'] # Add other editable fields like bio if you add it to Profile model