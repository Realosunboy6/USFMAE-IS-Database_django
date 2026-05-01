from django import template

from finance.rbac import user_has_finance_perm

register = template.Library()


@register.simple_tag(takes_context=True)
def finance_can(context, codename):
    request = context["request"]
    return user_has_finance_perm(request.user, codename)
