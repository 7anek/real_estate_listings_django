from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):

    confirmation_token = models.UUIDField(blank=True, null=True)
    is_verified = models.BooleanField(default=False, blank=True, null=True)
    email = models.EmailField(unique=True, null=False)