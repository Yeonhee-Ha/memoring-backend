from django.db import models
from user.models import User
# Create your models here.

# 일정 등록
class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    AM_PM_CHOICES = [
        ('AM', '오전'),
        ('PM', '오후')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voice_url = models.URLField()
    transcript = models.TextField()
    parsed_title = models.CharField(max_length=255)
    parsed_date = models.DateField()
    parsed_time = models.TimeField()
    parsed_ampm = models.CharField(max_length=2, choices=AM_PM_CHOICES)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

#스케줄 상태
class ScheduleStats(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    registered_count = models.IntegerField(default=0)
    completed_count = models.IntegerField(default=0)

#브리핑 음성
class BriefingVoice(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    briefing_text = models.TextField()
    briefing_voice_url = models.URLField()
    updated_at = models.DateTimeField(auto_now=True)
    