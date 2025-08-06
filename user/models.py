from django.db import models
from django.contrib.auth.models import AbstractUser

#이미지를 유저별로 디렉터리를 분리해 저장할 수 있음
#def image_upload_path(instance, filename):
#    return f'user/{instance.id}/profile/{filename}'

# 사용자 모델
class User(AbstractUser):
    username = None  # username 필드 제거
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True) #아이디로 사용하려면 unique로 설정해야 함
    name = models.CharField(max_length=50) #기존 방식은 성, 이름을 따로 입력해야 함
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    tutorial_status = models.BooleanField(default=False)
    image = models.URLField(blank=True, null=True) #외부 url을 저장하는 방식
    #image = models.ImageField(upload_to=image_upload_path, blank=True, null=True) 실제 파일 업로드

    USERNAME_FIELD = 'email' #로그인 시 사용할 필드 지정: 이메일을 아이디로 사용함
    REQUIRED_FIELDS = [] #createsuperuser 명령어에서 추가로 입력을 요구할 필드 목록

# 설정 모델
class Setting(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sleep_start = models.TimeField()
    sleep_end = models.TimeField()
    voice_url = models.URLField()
    voice_id = models.CharField(max_length=255)
    reminder_time = models.TimeField()

    

