"""Record sensitive finance writes aligned with authenticated staff context."""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .middleware import current_audit_actor
from .models import ActionItem, AidApplication, ApplicationDocument, AuditLog, Payment, StudentCharge


def write_audit_log(instance, *, model_label: str, action: str, summary: str, student):
    AuditLog.objects.create(
        actor=current_audit_actor(),
        student=student,
        action=action,
        object_type=model_label,
        object_id=str(instance.pk),
        summary=summary,
    )


@receiver(post_save, sender=Payment)
def audit_payment(sender, instance, created, **kwargs):
    verb = created and AuditLog.Action.CREATE or AuditLog.Action.UPDATE
    summary = f"Receipt {instance.receipt_no}: ${instance.amount}"
    write_audit_log(instance, model_label="Payment", action=verb, summary=summary, student=instance.student)


@receiver(post_save, sender=StudentCharge)
def audit_student_charge(sender, instance, created, **kwargs):
    verb = created and AuditLog.Action.CREATE or AuditLog.Action.UPDATE
    fee_label = getattr(instance.fee, "fee_name", "fee record")
    summary = (
        f"Charge {fee_label} (${instance.amount}) for student {instance.student.student_id}; due {instance.due_date}"
    )
    write_audit_log(instance, model_label="StudentCharge", action=verb, summary=summary, student=instance.student)


@receiver(post_save, sender=AidApplication)
def audit_aid_application(sender, instance, created, **kwargs):
    verb = created and AuditLog.Action.CREATE or AuditLog.Action.UPDATE
    summary = f"Aid application {instance.application_id}: status {instance.get_status_display()}"
    write_audit_log(instance, model_label="AidApplication", action=verb, summary=summary, student=instance.student)


@receiver(post_save, sender=ActionItem)
def audit_action_item(sender, instance, created, **kwargs):
    verb = created and AuditLog.Action.CREATE or AuditLog.Action.UPDATE
    summary = f'Action “{instance.title}” ({instance.get_status_display()})'
    write_audit_log(instance, model_label="ActionItem", action=verb, summary=summary, student=instance.student)


@receiver(post_save, sender=ApplicationDocument)
def audit_application_document(sender, instance, created, **kwargs):
    verb = created and AuditLog.Action.CREATE or AuditLog.Action.UPDATE
    summary = f'Checklist “{instance.required_document}” ({instance.get_status_display()}) — application {instance.application_id}'
    write_audit_log(
        instance,
        model_label="ApplicationDocument",
        action=verb,
        summary=summary,
        student=instance.application.student,
    )
    instance.application.sync_documents_submitted_flag()


@receiver(post_delete, sender=ApplicationDocument)
def refresh_application_documents_after_delete(sender, instance, **kwargs):
    summary = (
        "Removed checklist slot "
        f"document_id={instance.required_document_id}, application={instance.application_id}"
    )
    application = AidApplication.objects.select_related("student").filter(pk=instance.application_id).first()

    student = getattr(application, "student", None) if application else None
    if student:
        write_audit_log(
            instance,
            model_label="ApplicationDocument",
            action=AuditLog.Action.DELETE,
            summary=summary,
            student=student,
        )
    if application:
        application.sync_documents_submitted_flag()
