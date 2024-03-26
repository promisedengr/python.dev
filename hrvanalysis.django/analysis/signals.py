from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.db import transaction
from django.dispatch import receiver
from .models import Result, Sample
from .tasks import compute_result

@receiver(post_save, sender=Sample)
def create_result(sender, instance, created, **kwargs):
	if created:
		transaction.on_commit(lambda: compute_result.delay(instance.pk))

@receiver(post_save, sender=Result)
def send_new_result_notification_email(sender, instance, created, **kwargs):
	if created:
		user = instance.sample.subject.user
		subject = 'New analysis results'
		message = render_to_string('analysis/result-saved-email.html', {
			'user': user,
			'comment': instance.sample.comment
		})
		user.email_user(subject, message)