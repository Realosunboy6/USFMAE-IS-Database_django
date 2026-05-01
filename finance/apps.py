from django.apps import AppConfig


def bootstrap_finance_rbac(sender, **kwargs):
    app_config = kwargs.get("app_config")
    if app_config is None or app_config.label != "finance":
        return
    from finance.rbac import provision_default_staff_groups, setup_finance_groups

    setup_finance_groups()
    provision_default_staff_groups()


class FinanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finance"

    def ready(self):
        from django.db.models.signals import post_migrate

        post_migrate.connect(bootstrap_finance_rbac, dispatch_uid="finance.bootstrap_rbac")
        from . import signals  # noqa: F401 - register Django signals side effects.
