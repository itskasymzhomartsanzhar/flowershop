from celery import shared_task


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={'max_retries': 5})
def send_payment_reminder_task(self, payment_session_id, check_due=True):
    from .views import _try_send_payment_reminder

    return _try_send_payment_reminder(payment_session_id, check_due=bool(check_due))
