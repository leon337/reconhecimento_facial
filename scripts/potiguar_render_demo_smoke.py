"""Read-only HTTP security smoke for the isolated Render Potiguar demo.

Never call against production or any domain except the exact synthetic service.
"""
import http.cookiejar
import json
import urllib.error
import urllib.request

BASE = "https://potiguar-v2-demo-backend.onrender.com"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def smoke(base=BASE):
    if base != BASE:
        raise ValueError("Only the isolated synthetic Render domain is authorized")
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
        NoRedirect(),
    )

    def read(path):
        req = urllib.request.Request(base + path, headers={"User-Agent": "PotiguarSyntheticReadOnlySmoke/1"})
        try:
            response = opener.open(req, timeout=100)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = response.read(20000)
            return response.status, response.headers, body

    status, headers, page = read("/admin/copilot")
    assert status == 200, ("copilot", status)
    assert headers.get("X-Potiguar-Demo") == "synthetic-no-login"
    assert b"DEMONSTRA" in page.upper(), "missing synthetic demo label"

    status, headers, meta_body = read("/admin/copilot/meta")
    assert status == 200 and headers.get("X-Potiguar-Demo") == "synthetic-no-login"
    meta = json.loads(meta_body)
    assert meta.get("public_demo_no_login") is True
    assert meta.get("configured") is False, "permanent Gemini key must remain absent"

    status, headers, _ = read("/static/uploads/any.jpg")
    assert status == 403 and headers.get("X-Potiguar-Demo") == "synthetic-no-login"

    status, headers, _ = read("/admin/login")
    assert status == 302 and headers.get("Location") == "/admin/copilot"

    return {"status": "PASS", "url": base + "/admin/copilot", "checks": 8, "records_created": False}


if __name__ == "__main__":
    print(json.dumps(smoke(), ensure_ascii=False))
