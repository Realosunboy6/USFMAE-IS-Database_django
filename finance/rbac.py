"""Finance feature permissions backed by Django groups and custom codenames."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class FinancePermissions:
    """Permission codenames defined on FinanceDivision."""

    ACCESS_DASHBOARD = "access_dashboard"
    VIEW_STUDENT_DIRECTORY = "view_student_directory"
    MANAGE_BILLING = "manage_billing"
    MANAGE_AID = "manage_aid"
    MANAGE_ACTION_ITEMS = "manage_action_items"
    VIEW_REPORTS = "view_reports"
    VIEW_AUDIT_LOG = "view_audit_log"
    FULL_SUPERVISION = "full_supervision"
    SYSTEM_ADMIN = "system_admin"


META_PERMISSIONS = (FinancePermissions.FULL_SUPERVISION, FinancePermissions.SYSTEM_ADMIN)

GROUP_SUPERVISOR = "USFMAE Supervisor"
GROUP_SYSTEM_ADMIN = "USFMAE System Admin"
GROUP_BURSAR = "USFMAE Bursar Staff"
GROUP_FINANCIAL_AID = "USFMAE Financial Aid Reviewer"
GROUP_AUDITOR = "USFMAE Auditor"

_LEGACY_PREFIX = "USFMAE "


def finance_perm_label(codename: str) -> str:
    return f"finance.{codename}"


def user_has_finance_perm(user, codename: str) -> bool:
    if not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    for meta in META_PERMISSIONS:
        if user.has_perm(finance_perm_label(meta)):
            return True
    return user.has_perm(finance_perm_label(codename))


def _finance_perm_content_type():
    return ContentType.objects.get(app_label="finance", model="financedivision")


def assign_group_permissions(group_name: str, codenames: list[str]) -> Group:
    ct = _finance_perm_content_type()
    perms = Permission.objects.filter(content_type=ct, codename__in=codenames)
    group, _ = Group.objects.get_or_create(name=group_name)
    group.permissions.set(perms)
    return group


def setup_finance_groups() -> None:
    FP = FinancePermissions
    assign_group_permissions(
        GROUP_BURSAR,
        [FP.ACCESS_DASHBOARD, FP.VIEW_STUDENT_DIRECTORY, FP.MANAGE_BILLING, FP.VIEW_REPORTS],
    )
    assign_group_permissions(
        GROUP_FINANCIAL_AID,
        [
            FP.ACCESS_DASHBOARD,
            FP.VIEW_STUDENT_DIRECTORY,
            FP.MANAGE_AID,
            FP.MANAGE_ACTION_ITEMS,
            FP.VIEW_REPORTS,
        ],
    )
    assign_group_permissions(
        GROUP_AUDITOR,
        [FP.ACCESS_DASHBOARD, FP.VIEW_STUDENT_DIRECTORY, FP.VIEW_REPORTS, FP.VIEW_AUDIT_LOG],
    )
    supervisor_codes = [
        FP.ACCESS_DASHBOARD,
        FP.VIEW_STUDENT_DIRECTORY,
        FP.MANAGE_BILLING,
        FP.MANAGE_AID,
        FP.MANAGE_ACTION_ITEMS,
        FP.VIEW_REPORTS,
        FP.VIEW_AUDIT_LOG,
    ]
    assign_group_permissions(GROUP_SUPERVISOR, supervisor_codes + [FP.FULL_SUPERVISION])
    assign_group_permissions(GROUP_SYSTEM_ADMIN, supervisor_codes + [FP.SYSTEM_ADMIN])


def provision_default_staff_groups() -> None:
    """Attach the supervisor aggregate group to Django staff lacking an explicit USFMAE_* role."""

    User = get_user_model()
    try:
        supervisor = Group.objects.get(name=GROUP_SUPERVISOR)
    except Group.DoesNotExist:
        return

    qs = User.objects.filter(is_staff=True, is_superuser=False)
    for user in qs:
        if user.groups.filter(name__startswith=_LEGACY_PREFIX).exists():
            continue
        user.groups.add(supervisor)
