from django.db import models
from django.conf import settings

class RecallQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recall_questions")
    text = models.CharField(max_length=255)                 # 질문 내용
    answer_key = models.CharField(max_length=255, blank=True, null=True)  # 정답 키워드/문구
    difficulty = models.PositiveSmallIntegerField(default=1) # 1~5 정도 가정
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.id}] {self.text}"

class RecallAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recall_answers")
    question = models.ForeignKey(RecallQuestion, on_delete=models.CASCADE, related_name="answers")
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    response_time_sec = models.FloatField(default=0.0)      # 초 단위
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"A:{self.id} Q:{self.question_id}"



# 기존 코드

# from django.db import models
# from user.models import User

# class RecallQuestion(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     question_text = models.TextField()
#     audio_url = models.URLField()
#     created_at = models.DateTimeField(auto_now_add=True)

# class RecallAnswer(models.Model):
#     id = models.AutoField(primary_key=True)
#     recall_question = models.ForeignKey(RecallQuestion, on_delete=models.CASCADE)
#     voice_url = models.URLField()
#     transcript = models.TextField()
#     response_time = models.FloatField()
#     word_count = models.IntegerField()
#     repetition_count = models.IntegerField()
#     success = models.BooleanField()
#     created_at = models.DateTimeField(auto_now_add=True)

# class RecallReport(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     total_questions = models.IntegerField(default=0)
#     total_responses = models.IntegerField(default=0)
#     avg_response_time = models.FloatField(default=0.0)
#     avg_word_count = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
