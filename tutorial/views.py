from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import TutorialSerializer, SettingReadSerializer, SettingWriteSerializer
from .models import Setting, Voice

class TutorialViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # GET /tutorial/
    def list(self, request):
        serializer = TutorialSerializer(request.user)
        return Response(serializer.data)

    # POST /tutorial/
    def create(self, request):
        serializer = TutorialSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#######################################################
class SettingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # GET /tutorial/setting/
    def list(self, request):
        try:
            setting = request.user.setting
            serializer = SettingReadSerializer(setting)
            return Response(serializer.data)
        except Setting.DoesNotExist:
            return Response({"detail": "설정이 없습니다."}, status=404)

    # POST /tutorial/setting/ → 설정 생성/업데이트
    def create(self, request):
        try:
            setting = request.user.setting
            serializer = SettingWriteSerializer(setting, data=request.data, partial=True, context={"request": request})
        except Setting.DoesNotExist:
            serializer = SettingWriteSerializer(data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # POST /tutorial/setting/sleep
    @action(detail=False, methods=["post"], url_path="sleep")
    def set_sleep(self, request):
        try:
            setting = request.user.setting
        except Setting.DoesNotExist:
            setting = Setting(user=request.user)

        serializer = SettingWriteSerializer(
            setting, 
            data={
                "sleep_start": request.data.get("sleep_start"),
                "sleep_end": request.data.get("sleep_end")
            },
            partial=True
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # POST /tutorial/setting/voice
    @action(detail=False, methods=["post"], url_path="voice")
    def set_voice(self, request):
        try:
            setting = request.user.setting
        except Setting.DoesNotExist:
            setting = Setting(user=request.user)

        # 업로드된 파일 받기
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"detail": "파일이 필요합니다."}, status=400)

        # Voice 객체 생성
        voice_obj = Voice.objects.create(file=uploaded_file)

        # Setting에 연결
        setting.voice = voice_obj
        setting.save()

        serializer = SettingWriteSerializer(setting)
        return Response(serializer.data)
    
    # POST /tutorial/setting/reminder
    @action(detail=False, methods=["post"], url_path="reminder")
    def set_reminder(self, request):
        try:
            setting = request.user.setting
            serializer = SettingWriteSerializer(setting, data=request.data, partial=True)
        except Setting.DoesNotExist:
            serializer = SettingWriteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            # 저장 후 read serializer로 반환
            read_serializer = SettingReadSerializer(serializer.instance)
            return Response(read_serializer.data)
        return Response(serializer.errors, status=400)