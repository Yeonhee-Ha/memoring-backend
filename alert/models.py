from django.db import models
from user.models import User

# Create your models here.
# 리마인드 음성
class RemindVoice(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remind_text = models.TextField()
    remind_voice_url = models.URLField()
    updated_at = models.DateTimeField(auto_now=True)