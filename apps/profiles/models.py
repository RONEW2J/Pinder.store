from django.db import models
from django.conf import settings # Use settings.AUTH_USER_MODEL
from django.contrib.gis.db import models as gis_models # Import PointField from GeoDjango, aliased to avoid conflict

# Helper function for upload_to path
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    # or MEDIA_ROOT/profile_<id>/<filename>
    return f'profile_photos/profile_{instance.profile.id}/{filename}'
# Alternatively, you can use:
# from django.contrib.auth import get_user_model
# User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )  # Расширение данных пользователя
    age = models.PositiveIntegerField(null=True, blank=True) # Consider if age can be optional initially
    location = gis_models.PointField(geography=True, null=True, blank=True)  # GeoDjango - ensure PostGIS setup if using this
    interests = models.ManyToManyField('Interest', blank=True)

class Interest(models.Model): # You'll need to define the Interest model
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Photo(models.Model):
    profile = models.ForeignKey(Profile, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path)
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_profile_picture = models.BooleanField(default=False) # Optional: to mark one as the main display picture
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0) # Optional: for ordering photos

    class Meta:
        ordering = ['order', 'uploaded_at'] # Default ordering
