from app.observability import LoginRateLimiter


def test_security_headers_and_request_id(client):
    response = client.get("/health", headers={"X-Request-ID": "req-test-1"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-1"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_health_checks_database(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["database"] == "ok"


def test_metrics_count_requests(client):
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.get_json()["http_requests_total"] >= 2


def test_rate_limiter_blocks_after_limit():
    limiter = LoginRateLimiter()
    key = "127.0.0.1:admin"

    assert limiter.blocked(key, limit=2, window_seconds=60) is False
    limiter.register_failure(key)
    limiter.register_failure(key)
    assert limiter.blocked(key, limit=2, window_seconds=60) is True
    limiter.clear(key)
    assert limiter.blocked(key, limit=2, window_seconds=60) is False


def test_not_found_uses_standard_error_contract(client):
    response = client.get("/rota-inexistente")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["error"] == "not_found"
    assert payload["request_id"]
