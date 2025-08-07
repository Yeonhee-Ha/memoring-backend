from rest_framework import serializers
from .models import *

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'password', 'phone', 'birth_date',
            'tutorial_status', 'image', 'created_at'
        ]
        read_only_fields = ['id', 'tutorial_status', 'image', 'created_at']


    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # 회원가입 시 Setting 객체 자동 생성
        Setting.objects.create(
            user=user,
            sleep_start="00:00:00",
            sleep_end="00:00:00",
            voice_url="",
            voice_id="",
            reminder_time="00:00:00",
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'birth_date', 'name', 'image']
        read_only_fields = ['id', 'email']