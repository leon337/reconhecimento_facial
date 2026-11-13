#!/usr/bin/env python3
"""Gera HTML real do Flask com dados sinteticos para teste de navegador isolado."""
import os
import json
from pathlib import Path
from tests.test_copilot_onboarding_runtime_unittest import CopilotOnboardingTests

fixture = CopilotOnboardingTests(methodName="test_iframe_security_and_microphone")
fixture.setUp()
created = fixture.client.get("/admin/onboarding/new")
assert created.status_code == 302, created.status_code
response = fixture.client.get(created.location)
assert response.status_code == 200, response.status_code
html = response.get_data(as_text=True)
assert "admin-onboarding-controller.js" in html
assert "onboarding-copilot-drawer" in html
output = Path(os.environ.get("POTIGUAR_E2E_HTML", "/tmp/potiguar-browser-e2e-20261113/index.html"))
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(html, encoding="utf-8")
embed = fixture.client.get('/admin/copilot/embed/onboarding')
assert embed.status_code == 200, embed.status_code
(output.parent / 'embed.html').write_text(embed.get_data(as_text=True), encoding='utf-8')
(output.parent / 'embed-headers.json').write_text(json.dumps({
    'csp': embed.headers.get('Content-Security-Policy', ''),
    'permissions': embed.headers.get('Permissions-Policy', ''),
    'x_frame_options': embed.headers.get('X-Frame-Options', ''),
}), encoding='utf-8')
print("fixture_ok", str(output), len(html), "embed", embed.status_code)
