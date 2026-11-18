#!/usr/bin/env python3
"""HTML sintético para E2E de UX: renderiza o template real sem Flask, banco ou segredos.

Uso:
  python3 scripts/potiguar_onboarding_ux_fixture.py
  POTIGUAR_PUPPETEER_MODULE=/caminho/puppeteer node scripts/potiguar_onboarding_ux_browser_e2e.cjs

Requer Jinja2 (dependência do Flask). O token CSRF e os IDs aqui são apenas marcadores.
"""
import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path("/tmp/potiguar-onboarding-ux-fixture.html")


def render_synthetic_demo() -> str:
    steps = runpy.run_path(str(ROOT / "app/onboarding_fields.py"))["STEPS"]
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=True)

    def url_for(endpoint, **options):
        if endpoint == "static":
            return "/static/" + options["filename"]
        paths = {
            "admin.list_users": "/admin/users",
            "admin.dashboard": "/admin/dashboard",
            "admin.history": "/admin/history",
            "admin.onboarding_drafts": "/admin/onboarding/drafts",
            "admin.onboarding_save": "/admin/onboarding/" + "a" * 32 + "/save",
            "admin.onboarding_complete": "/admin/onboarding/" + "a" * 32 + "/complete",
            "admin.onboarding_discard": "/admin/onboarding/" + "a" * 32 + "/discard",
            "copilot.onboarding_embed": "/admin/copilot/embed/onboarding",
        }
        return paths.get(endpoint, "/admin/fixture-only")

    env.globals.update(url_for=url_for, csrf_token=lambda: "TEST_CSRF_NOT_VALID")
    return env.get_template("admin/users_new_v2.html").render(
        draft=SimpleNamespace(id="a" * 32, version=0),
        steps=steps, saved={}, config={"PUBLIC_DEMO_MODE": True},
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    html = render_synthetic_demo()
    assert 'data-demo="1"' in html
    assert 'name="has_system_access"' in html
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"UX_FIXTURE_READY {args.output} ({len(html)} chars)")


if __name__ == "__main__":
    main()
