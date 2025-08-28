from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from .models import Schedule
from tutorial.models import Voice
from .serializers import ScheduleStepSerializer, ScheduleSerializer

import json
from datetime import datetime
import requests
from django.conf import settings
from openai import OpenAI
from django.conf import settings

# OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ElevenLabs TTS helper
def elevenlabs_tts(text: str, voice_id: str):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"TTS failed: {response.text}")

    file_path = f"{settings.MEDIA_ROOT}/tts/question.mp3"
    with open(file_path, "wb") as f:
        f.write(response.content)

    tts_url = settings.MEDIA_URL + "tts/question.mp3"
    return tts_url

    
def elevenlabs_tts_summary(text: str, voice_id: str, filename="summary.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"TTS failed: {response.text}")
    file_path = f"{settings.MEDIA_ROOT}/tts/{filename}"
    with open(file_path, "wb") as f:
        f.write(response.content)
    return settings.MEDIA_URL + f"tts/{filename}"

    
######################################################
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    QUESTIONS = [
        "어떤 일정인가요?",
        "몇 월 며칠 일정인가요?",
        "몇 시 일정인가요?",
        "오전인가요 오후인가요?"
    ]
    
    # 본인 일정만 조회
    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)

    # 진행 중인 일정 조회
    @action(detail=False, methods=["get"])
    def current(self, request):
        schedule = Schedule.objects.filter(user=request.user, processed=False).last()
        if not schedule:
            return Response({"error": "진행 중인 일정이 없습니다."}, status=404)
        return Response(self.get_serializer(schedule).data)
    
    # 1️⃣ 질문 단계 (TTS)
    @action(detail=False, methods=["get"])
    def question(self, request):
        step = int(request.query_params.get("step", 1))
        if step > len(self.QUESTIONS):
            return Response({"message": "질문이 끝났습니다."})

        question_text = self.QUESTIONS[step - 1]

        try:
            voice_id = request.user.voice.voice_id
        except Voice.DoesNotExist:
            return Response({"error": "Voice 설정이 없습니다."}, status=400)

        tts_url = elevenlabs_tts(question_text, voice_id)
        return Response({
            "step": step,
            "question": question_text,
            "tts_url": request.build_absolute_uri(tts_url)
        })
        
        
    # 2️⃣ 답변 업로드 (STT + GPT 파싱)
    @action(detail=False, methods=["post"])
    def answer(self, request):
        step = int(request.data.get("step", 1))
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "음성 파일 업로드 필요"}, status=400)

        # 1. Whisper STT
        with open(file.temporary_file_path(), "rb") as audio:
            transcript_obj = client.audio.transcriptions.create(model="whisper-1", file=audio)
        text = transcript_obj.text

        # 2. GPT 파싱 (step별)
        prompt_map = {
            1: f"사용자가 말한 일정 제목을 JSON으로 추출하세요: '{text}'\n{{'title': '...' }}",
            2: f"사용자가 말한 날짜를 JSON으로 추출하세요: '{text}'\n{{'date': 'YYYY-MM-DD'}}",
            3: f"사용자가 말한 시간을 JSON으로 추출하세요: '{text}'\n{{'time': 'HH:MM'}}",
            4: f"사용자가 말한 오전/오후를 JSON으로 추출하세요: '{text}'\n{{'ampm': 'AM' or 'PM'}}"
        }

        gpt_res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_map[step]}],
            temperature=0
        )
        parsed_text = gpt_res.choices[0].message["content"]
        parsed_json = json.loads(parsed_text)

        # 3. Schedule 객체 가져오기/생성
        schedule, _ = Schedule.objects.get_or_create(user=request.user, processed=False)

        # 4. step별 필드 업데이트
        if step == 1:
            schedule.parsed_title = parsed_json.get("title")
        elif step == 2:
            schedule.parsed_date = datetime.strptime(parsed_json.get("date"), "%Y-%m-%d").date()
        elif step == 3:
            schedule.parsed_time = datetime.strptime(parsed_json.get("time"), "%H:%M").time()
        elif step == 4:
            schedule.parsed_ampm = parsed_json.get("ampm")

        schedule.transcript = (schedule.transcript or "") + f"\nQ{step}: {text}"
        schedule.save()

        return Response({
            "step": step, 
            "transcript": text, 
            "parsed": parsed_json,
            "schedule": ScheduleSerializer(schedule).data,
        })

        
    # 3️⃣ 최종 저장
    @action(detail=False, methods=["post"])
    def confirm(self, request, pk=None):
        schedule = Schedule.objects.filter(user=request.user, processed=False).last()
        if not schedule:
            return Response({"error": "저장할 일정이 없습니다."}, status=400)

        # ✅ 2.1.4 일정 수정 기능
        # 프론트에서 수정이 있었다면 반영 가능
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

        # ✅ 2.1.3 일정 요약 TTS
        summary_text = f"일정: {schedule.parsed_title}, 날짜: {schedule.parsed_date}, 시간: {schedule.parsed_time}, 오전/오후: {schedule.parsed_ampm}"
        try:
            voice_id = request.user.voice.voice_id
            tts_url = elevenlabs_tts_summary(summary_text, voice_id)
        except Exception:
            tts_url = None

        schedule.processed = True
        schedule.save()

        return Response({
            "schedule": ScheduleSerializer(schedule).data,
            "summary_text": summary_text,
            "tts_url": request.build_absolute_uri(tts_url) if tts_url else None
        })

    # DELETE /schedule/{pk}/
    def destroy(self, request, pk=None):
        try:
            schedule = Schedule.objects.get(pk=pk, user=request.user)
        except Schedule.DoesNotExist:
            return Response({"error": "해당 일정이 없습니다."}, status=404)
        schedule.delete()
        return Response({"message": "일정이 삭제되었습니다."}, status=204)