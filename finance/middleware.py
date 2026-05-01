"""Capture the authenticated user so ORM saves can associate audit trails."""

from __future__ import annotations

import threading

_thread_locals = threading.local()


class AuditActorMiddleware:
    """Store request.user during the HTTP request lifecycle."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        previous = getattr(_thread_locals, "user", None)
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            _thread_locals.user = user
        else:
            _thread_locals.user = None
        try:
            return self.get_response(request)
        finally:
            _thread_locals.user = previous


def current_audit_actor():
    return getattr(_thread_locals, "user", None)
