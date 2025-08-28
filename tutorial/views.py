from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import TutorialSerializer, SettingReadSerializer, SettingWriteSerializer
from .models import Setting, Voice
from datetime import time
import os, requests

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

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

        validated_data = serializer.validated_data.copy()
        voice_file = validated_data.pop("voice", None)

        # 1️⃣ Voice 생성/업데이트 + ElevenLabs 업로드
        voice_obj = None
        if voice_file:
            voice_obj, _ = Voice.objects.update_or_create(
                user=request.user,
                defaults={"file": voice_file}
            )

            # ElevenLabs 업로드
            with open(voice_obj.file.path, "rb") as f:
                files = {"voice_file": f}  # ElevenLabs 문서 기준
                headers = {"xi-api-key": ELEVENLABS_API_KEY}
                resp = requests.post("https://api.elevenlabs.io/v1/voices", headers=headers, files=files)

            if resp.status_code == 200:
                data = resp.json()
                voice_obj.voice_id = data.get("voice_id")
                voice_obj.save()
            else:
                return Response({"detail": "ElevenLabs 업로드 실패"}, status=resp.status_code)

        # 2️⃣ reminder_time 처리
        reminder = validated_data.pop("reminder_time", None)
        if reminder is not None:
            validated_data["reminder_time"] = time(hour=reminder // 60, minute=reminder % 60)

        # 3️⃣ Setting 생성/업데이트
        setting, _ = Setting.objects.update_or_create(
            user=request.user,
            defaults=validated_data
        )

        # 4️⃣ ReadSerializer로 응답
        return Response(SettingReadSerializer(setting, context={"request": request}).data,
                        status=status.HTTP_200_OK)

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

        # 1. Voice DB 저장 (파일)
        voice_obj, _ = Voice.objects.update_or_create(
            user=request.user,
            defaults={"file": uploaded_file}
        )

        # 2. ElevenLabs 업로드
        with open(voice_obj.file.path, "rb") as f:
            files = {"voice_file": f}  # ElevenLabs 문서에 따라 키 확인
            headers = {"xi-api-key": ELEVENLABS_API_KEY}
            resp = requests.post("https://api.elevenlabs.io/v1/voices", headers=headers, files=files)
        
        if resp.status_code == 200:
            data = resp.json()
            voice_obj.voice_id = data.get("voice_id")
            voice_obj.save()
        else:
            return Response({"detail": "ElevenLabs 업로드 실패"}, status=resp.status_code)

        # 3. Setting도 함께 가져오기/생성
        setting, _ = Setting.objects.update_or_create(user=request.user)

        # 4. 최종 Response
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
