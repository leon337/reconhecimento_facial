import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from threading import Lock
from uuid import uuid4

from flask import current_app, g, jsonify, request, session
from sqlalchemy import text

from app.audit_models import AuditEvent
from app.models import db


class LoginRateLimiter:
    """Limitador simples por identidade e IP; adequado ao processo único atual."""

    def __init__(self):
        self._attempts = defaultdict(deque)
        self._lock = Lock()

    def blocked(self, key: str, *, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            attempts = self._attempts[key]
            while attempts and attempts[0] < cutoff:
                attempts.popleft()
            return len(attempts) >= limit

    def register_failure(self, key: str) -> None:
        with self._lock:
            self._attempts[key].append(time.monotonic())

    def clear(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)


login_rate_limiter = LoginRateLimiter()
_metrics = defaultdict(int)
_metrics_lock = Lock()


def increment_metric(name: str) -> None:
    with _metrics_lock:
        _metrics[name] += 1


def _request_id() -> str:
    request_id = getattr(g, "request_id", None)
    if request_id is None:
        request_id = request.headers.get("X-Request-ID") or uuid4().hex
        g.request_id = request_id
    return request_id


def audit(action: str, outcome: str, *, actor=None, target_type=None, target_id=None, metadata=None):
    safe_metadata = metadata or {}
    event = AuditEvent(
        request_id=_request_id(),
        action=action,
        outcome=outcome,
        actor_user_id=getattr(actor, "id", None),
        company_id=session.get("admin_company_id"),
        worksite_id=session.get("admin_worksite_id"),
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        remote_addr=request.headers.get("X-Forwarded-For", request.remote_addr),
        metadata_json=json.dumps(safe_metadata, sort_keys=True),
    )
    db.session.add(event)
    return event


def init_observability(app):
    app.config.setdefault("LOGIN_RATE_LIMIT_ATTEMPTS", 5)
    app.config.setdefault("LOGIN_RATE_LIMIT_WINDOW_SECONDS", 300)
    app.config.setdefault("PERMANENT_SESSION_LIFETIME", timedelta(minutes=30))

    @app.before_request
    def assign_request_id():
        g.request_id = request.headers.get("X-Request-ID") or uuid4().hex
        g.request_started_at = time.monotonic()
        increment_metric("http_requests_total")

    @app.after_request
    def secure_response(response):
        request_id = _request_id()
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(self), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; frame-ancestors 'none'"
        )
        if current_app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        started_at = getattr(g, "request_started_at", time.monotonic())
        duration_ms = int((time.monotonic() - started_at) * 1000)
        current_app.logger.info(
            json.dumps({
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            }, sort_keys=True)
        )
        return response

    @app.errorhandler(404)
    def not_found(error):
        increment_metric("http_errors_total")
        return jsonify(error="not_found", request_id=_request_id()), 404

    @app.errorhandler(500)
    def internal_error(error):
        increment_metric("http_errors_total")
        request_id = _request_id()
        current_app.logger.exception("internal_error request_id=%s", request_id)
        db.session.rollback()
        return jsonify(error="internal_error", request_id=request_id), 500

    @app.get("/health")
    def health():
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok", database="ok", timestamp=datetime.utcnow().isoformat() + "Z")

    @app.get("/metrics")
    def metrics():
        with _metrics_lock:
            snapshot = dict(_metrics)
        return jsonify(snapshot)

    if not app.logger.handlers:
        handler = logging.StreamHandler()
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
