from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


# 회원가입용 (비밀번호 write_only 처리)
class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "name", "phone", "birth_date", "tutorial_status", "image"]

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            name=validated_data["name"],
            phone=validated_data["phone"],
            birth_date=validated_data["birth_date"],
            tutorial_status=validated_data.get("tutorial_status", False),
            image=validated_data.get("image"),
        )
        user.set_password(validated_data["password"])  # 비밀번호 해싱
        user.save()
        return user


# 유저 조회/수정/응답 공용
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "phone", "birth_date", "created_at", "tutorial_status", "image"]
        read_only_fields = ["id", "email", "created_at"]
