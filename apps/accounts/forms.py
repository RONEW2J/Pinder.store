from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    # Define the custom fields that are part of your User model
    # and you want to include in the registration form.

    # Assuming 'birth_date' is a DateField on your User model
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False # Make it optional if desired
    )
    age = forms.IntegerField(
        required=False, # Make it optional if desired
        label="Age",
        min_value=18 # Example: ensure user is at least 18
    )

    # Assuming 'gender' is a CharField with choices on your User model
    # The choices will be automatically picked up from the model field.
    # If you need to override or specify choices here:
    # gender = forms.ChoiceField(choices=User.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    # Assuming 'interested_in' is a CharField with choices on your User model
    # interested_in = forms.ChoiceField(choices=User.INTERESTED_IN_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        # UserCreationForm.Meta.fields typically includes 'username' and password fields.
        # We add our custom fields to this tuple.
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email',
            'birth_date', 'gender', 'interested_in',
        )
        # Example of explicitly setting all fields if UserCreationForm.Meta.fields is not suitable:
        # fields = ('username', 'email', 'first_name', 'last_name', 'birth_date', 'gender', 'interested_in', 'password2', 'password2')

        # If your User model doesn't use 'username', you might need to adjust UserCreationForm.Meta.fields
        # or ensure 'username' is also in the tuple above if it's required.
        # For example, if email is the username field, UserCreationForm needs to be customized more deeply
        # or you'd use a different base form.