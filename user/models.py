from django.db import models
from django.contrib.auth.models import AbstractUser

# 사용자 모델
class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()
    tutorial_status = models.BooleanField(default=False)
    image = models.URLField(blank=True, null=True)


# 설정 모델
class Setting(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sleep_start = models.TimeField()
    sleep_end = models.TimeField()
    voice_url = models.URLField()
    voice_id = models.CharField(max_length=255)
    reminder_time = models.TimeField()

