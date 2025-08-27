from django.db import models
from user.models import User

from django.db import models
from user.models import User

class Voice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 유저당 1개 Voice
    file = models.FileField(upload_to="voices/")
    
    def __str__(self):
        return f"{self.user.name} Voice"

# 설정 모델
class Setting(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sleep_start = models.TimeField()
    sleep_end = models.TimeField()
    reminder_time = models.TimeField()
    
    def __str__(self):
        return f"[{self.id}] {self.user.name} / ({self.sleep_start} - {self.sleep_end})"

