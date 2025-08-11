from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.templatetags.static import static



class CustomUser(AbstractUser):

    address = models.CharField(max_length=200, blank=True, null=True)
    detail_address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)


