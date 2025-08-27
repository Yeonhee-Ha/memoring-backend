from django.db import models
from django.contrib.auth.models import AbstractUser

#이미지를 유저별로 디렉터리를 분리해 저장할 수 있음
#def image_upload_path(instance, filename):
#    return f'user/{instance.id}/profile/{filename}'

# 사용자 모델
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# 1️⃣ 커스텀 유저 매니저
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser는 is_staff=True 이어야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser는 is_superuser=True 이어야 합니다.")

        return self.create_user(email, password, **extra_fields)


# 2️⃣ 커스텀 유저 모델
class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    tutorial_status = models.BooleanField(default=False)
    image = models.URLField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["birth_date", "name", "phone"]  # createsuperuser 시 추가 필드 요구하지 않음

    objects = UserManager()  # 커스텀 매니저 연결

##################################################################3

