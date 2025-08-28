from rest_framework import serializers
from .models import Setting, Voice
from user.models import User
from datetime import time,timedelta

# 유저 정보 끌어오기
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "phone", "birth_date", "image"]

class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = ["id", "file"]

#################################################

class SettingReadSerializer(serializers.ModelSerializer):
    user_info = UserInfoSerializer(source="user", read_only=True)
    voice = serializers.SerializerMethodField()
    reminder_time = serializers.SerializerMethodField()

    class Meta:
        model = Setting
        fields = ["sleep_start", "sleep_end", "reminder_time", "voice", "user_info"]

    def get_reminder_time(self, obj):
        if obj.reminder_time is None:
            return None
        return obj.reminder_time.hour * 60 + obj.reminder_time.minute

    def get_voice(self, obj):
        try:
            voice = obj.user.voice
            return VoiceSerializer(voice).data
        except Voice.DoesNotExist:
            return None

class SettingWriteSerializer(serializers.ModelSerializer):
    voice = serializers.FileField(required=False)
    reminder_time = serializers.IntegerField(required=False)
    sleep_start = serializers.CharField()
    sleep_end = serializers.CharField()

    class Meta:
        model = Setting
        fields = ["sleep_start", "sleep_end", "reminder_time", "voice"]

    def validate_time_field(self, value):
        if isinstance(value, int):
            return time(hour=value)
        if isinstance(value, str):
            if ":" in value:
                parts = value.split(":")
                return time(hour=int(parts[0]), minute=int(parts[1]))
            else:
                # 숫자 문자열 "22" 같은 경우
                return time(hour=int(value))
        raise serializers.ValidationError("Time must be 'HH:MM' string or int hour.")

    def validate(self, attrs):
        if "sleep_start" in attrs:
            attrs["sleep_start"] = self.validate_time_field(attrs["sleep_start"])
        if "sleep_end" in attrs:
            attrs["sleep_end"] = self.validate_time_field(attrs["sleep_end"])
        # reminder_time는 문자열로 와도 int 변환
        if "reminder_time" in attrs and isinstance(attrs["reminder_time"], str):
            attrs["reminder_time"] = int(attrs["reminder_time"])
        return attrs

    def create(self, validated_data):
        # validated_data 안에 'user'가 들어 있을 수 있으므로 제거
        validated_data.pop("user", None)  

        user = self.context["request"].user
        voice = validated_data.pop("voice", None)

        if voice:
            from .models import Voice
            Voice.objects.update_or_create(user=user, defaults={"file": voice})

        reminder = validated_data.pop("reminder_time", None)
        if reminder is not None:
            validated_data["reminder_time"] = time(hour=reminder // 60, minute=reminder % 60)

        return Setting.objects.create(user=user, **validated_data)


    def update(self, instance, validated_data):
        voice = validated_data.pop("voice", None)
        if voice:
            from .models import Voice
            Voice.objects.update_or_create(user=instance.user, defaults={"file": voice})

        reminder = validated_data.pop("reminder_time", None)
        if reminder is not None:
            instance.reminder_time = time(hour=reminder // 60, minute=reminder % 60)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

#########################################################

class TutorialSerializer(serializers.ModelSerializer):
    setting = SettingReadSerializer(read_only=True)
    user_info = UserInfoSerializer(source="user", read_only=True)  # ✅ 수정됨

    class Meta:
        model = User
        fields = ["tutorial_status", "user_info", "setting"]
