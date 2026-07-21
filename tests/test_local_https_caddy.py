from pathlib import Path


def test_caddy_defines_default_sni_for_ip_clients():
    caddyfile = Path("Caddyfile.local").read_text(encoding="utf-8")

    assert "default_sni {$LAN_IP}" in caddyfile
    assert "https://{$LAN_IP}:8443" in caddyfile
    assert "tls internal" in caddyfile


def test_local_compose_exposes_https_proxy_ports():
    compose = Path("docker-compose.local.yml").read_text(encoding="utf-8")

    assert '"8080:8080"' in compose
    assert '"8443:8443"' in compose
