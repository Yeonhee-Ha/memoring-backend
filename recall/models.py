from django.db import models
from user.models import User

class RecallQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    audio_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

class RecallAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    recall_question = models.ForeignKey(RecallQuestion, on_delete=models.CASCADE)
    voice_url = models.URLField()
    transcript = models.TextField()
    response_time = models.FloatField()
    word_count = models.IntegerField()
    repetition_count = models.IntegerField()
    success = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

class RecallReport(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_questions = models.IntegerField(default=0)
    total_responses = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0.0)
    avg_word_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
