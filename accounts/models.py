# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('demo', 'Demo (3 uploads/month)'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='demo')

    uploads_this_month = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} Profile"
