from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import TutorialSerializer, SettingReadSerializer, SettingWriteSerializer
from .models import Setting, Voice
from datetime import time

class TutorialViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # GET /tutorial/
    def list(self, request):
        serializer = TutorialSerializer(request.user)
        return Response(serializer.data)

    # POST /tutorial/ → tutorial_status 업데이트
    def create(self, request):
        serializer = TutorialSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


#######################################################
class SettingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SettingReadSerializer
        return SettingWriteSerializer

    # GET /tutorial/setting/
    def list(self, request):
        try:
            setting = request.user.setting
        except Setting.DoesNotExist:
            return Response({"detail": "설정이 없습니다."}, status=404)

        serializer = SettingReadSerializer(setting, context={"request": request})
        return Response(serializer.data)

    # POST /tutorial/setting/ → create or update
    def create(self, request):
        serializer = SettingWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # update_or_create 사용
        validated_data = serializer.validated_data.copy()
        voice_file = validated_data.pop("voice_file", None)

        if voice_file:
            Voice.objects.update_or_create(user=request.user, defaults={"file": voice_file})

        reminder = validated_data.pop("reminder_time", None)
        if reminder is not None:
            validated_data["reminder_time"] = time(hour=reminder // 60, minute=reminder % 60)

        setting, _ = Setting.objects.update_or_create(
            user=request.user,
            defaults=validated_data
        )

        read_serializer = SettingReadSerializer(setting, context={"request": request})
        return Response(read_serializer.data)

    # POST /tutorial/setting/sleep → create or update sleep times
    @action(detail=False, methods=["post"], url_path="sleep")
    def set_sleep(self, request):
        serializer = SettingWriteSerializer(data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data.copy()
        reminder = validated_data.pop("reminder_time", None)
        if reminder is not None:
            validated_data["reminder_time"] = time(hour=reminder // 60, minute=reminder % 60)

        setting, _ = Setting.objects.update_or_create(
            user=request.user,
            defaults=validated_data
        )

        return Response(SettingReadSerializer(setting, context={"request": request}).data)

    # POST /tutorial/setting/voice → create or update voice
    @action(detail=False, methods=["post"], url_path="voice")
    def set_voice(self, request):
        uploaded_file = request.FILES.get("voice")
        if not uploaded_file:
            return Response({"detail": "파일이 필요합니다."}, status=400)

        Voice.objects.update_or_create(user=request.user, defaults={"file": uploaded_file})

        setting, _ = Setting.objects.update_or_create(user=request.user)
        return Response(SettingReadSerializer(setting, context={"request": request}).data)

    # POST /tutorial/setting/reminder → create or update reminder
    @action(detail=False, methods=["post"], url_path="reminder")
    def set_reminder(self, request):
        serializer = SettingWriteSerializer(data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data.copy()
        reminder = validated_data.pop("reminder_time", None)
        if reminder is not None:
            validated_data["reminder_time"] = time(hour=reminder // 60, minute=reminder % 60)

        setting, _ = Setting.objects.update_or_create(
            user=request.user,
            defaults=validated_data
        )

        return Response(SettingReadSerializer(setting, context={"request": request}).data)
