from django.db import models
from user.models import User
from django.conf import settings

# Create your models here.

class Alert(models.Model):
    class Channel(models.TextChoices):
        MOCK = "mock", "Mock" 
        EMAIL = "email", "Email" # 확장 고려
        PUSH  = "push",  "Push"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT    = "sent",    "Sent"
        FAILED  = "failed",  "Failed"

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="alerts"
    )
    title = models.CharField(max_length=120)
    body = models.TextField(blank=True)
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.MOCK)

    send_at = models.DateTimeField(db_index=True) # 예약 시각(Asia/Seoul) 가정
    delivered_at = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    retries = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)

    # 선택 연동용
    schedule_id = models.IntegerField(blank=True, null=True) # schedule 미구현 상태 대비 (이후 주석)
    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-send_at"]

    def __str__(self):
        return f"[{self.id}] {self.title} ({self.status})"


# 리마인드 음성 기능은 Alert 기능과 별도이기에 일단 보류

# # 리마인드 음성
# class RemindVoice(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     remind_text = models.TextField()
#     remind_voice_url = models.URLField()
#     updated_at = models.DateTimeField(auto_now=True)