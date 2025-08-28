from django.utils import timezone
from .models import Alert

def send_alert(alert: Alert) -> Alert:
    
    # channel='mock'이면 콘솔 출력으로 전송 성공
    # 실패 시 status=failed, last_error 기록됨
    try:
        # 실제 구현은 채널별 분기(Firebase, 이메일 등) 추가해야 함
        if alert.channel == Alert.Channel.MOCK:
            print(f"[ALERT MOCK] to user={alert.user_id}, title={alert.title}, body={alert.body}")

        # 성공 처리
        alert.status = Alert.Status.SENT
        alert.delivered_at = timezone.now()
        alert.last_error = ""
        alert.save(update_fields=["status", "delivered_at", "last_error", "updated_at"])
        return alert

    except Exception as e:
        alert.status = Alert.Status.FAILED
        alert.retries += 1
        alert.last_error = str(e)[:1000]
        alert.save(update_fields=["status", "retries", "last_error", "updated_at"])
        return alert
