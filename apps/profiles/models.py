from django.db import models
from django.conf import settings # Use settings.AUTH_USER_MODEL

# Helper function for upload_to path
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    # or MEDIA_ROOT/profile_<id>/<filename>
    return f'profile_photos/profile_{instance.profile.id}/{filename}'
# Alternatively, you can use:
# from django.contrib.auth import get_user_model
# User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True, default="DEBUG_BIO_FIELD")
    interests = models.ManyToManyField('Interest', blank=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_visible = models.BooleanField(default=True)
 
    blocked_users = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='blocked_by'
    )
    
    matches = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='matched_with'
    )
    
    @property
    def main_image(self):
        main_photo = self.photos.filter(is_profile_avatar=True).first()
        if main_photo:
            return main_photo.image
        return None
            
        return None # Return None if no avatar and no other photos

class Interest(models.Model): # You'll need to define the Interest model
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Photo(models.Model):
    profile = models.ForeignKey(Profile, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_photos/')
    caption = models.CharField(max_length=255, blank=True, null=True) # Optional caption
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_profile_avatar = models.BooleanField(default=False, help_text="Is this the main profile picture?")


    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Photo for {self.profile.user.username} uploaded at {self.uploaded_at}"

class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # Optional: Add state/province, country if needed
    # state = models.CharField(max_length=100, blank=True, null=True)
    # country = models.CharField(max_length=100, blank=True, null=True)
    # Optional: Store latitude and longitude if you need them for simple map display
    # latitude = models.FloatField(null=True, blank=True)
    # longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"