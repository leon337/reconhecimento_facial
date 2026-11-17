"""Fail-closed environment tests for the isolated Render synthetic demo."""
import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet

from scripts.potiguar_render_demo_environment import (
    REQUIRED,
    prepare_render_demo_environment,
)


class RenderSyntheticDemoEnvironmentTest(unittest.TestCase):
    def base(self):
        return {
            **REQUIRED,
            "SECRET_KEY": "unit-test-only-" + ("x" * 48),
        }

    def test_valid_synthetic_environment_derives_stable_encryption(self):
        env = self.base()
        prepare_render_demo_environment(env)
        key1 = env["POTIGUAR_ONBOARDING_FERNET_KEY"]
        self.assertEqual(
            Fernet(key1.encode()).decrypt(Fernet(key1.encode()).encrypt(b"synthetic")),
            b"synthetic",
        )
        prepare_render_demo_environment(env)
        self.assertEqual(env["POTIGUAR_ONBOARDING_FERNET_KEY"], key1)

    def test_each_required_guard_is_fail_closed(self):
        for name in REQUIRED:
            with self.subTest(flag=name):
                env = self.base()
                del env[name]
                with self.assertRaisesRegex(RuntimeError, name):
                    prepare_render_demo_environment(env)

    def test_private_database_and_production_mode_rejected(self):
        for name, value in (
            ("DATABASE_URL", "postgresql://private.example/data"),
            ("APP_ENV", "production"),
            ("POTIGUAR_DEPLOYMENT_ROLE", "production"),
            ("POTIGUAR_PUBLIC_DEMO", "0"),
            ("POTIGUAR_HML_PUBLIC_HTTPS", "0"),
        ):
            with self.subTest(name=name):
                env = self.base()
                env[name] = value
                with self.assertRaises(RuntimeError):
                    prepare_render_demo_environment(env)

    def test_missing_or_weak_session_key_rejected(self):
        for secret in ("", "development-only-change-me", "too-short"):
            with self.subTest(length=len(secret)):
                env = self.base()
                env["SECRET_KEY"] = secret
                with self.assertRaises(RuntimeError):
                    prepare_render_demo_environment(env)

    def test_no_production_secrets_or_biometric_keys(self):
        for forbidden in ("GEMINI_API_KEY", "POTIGUAR_COPILOT_VAULT_DIR", "BIOMETRIC_ENCRYPTION_KEY"):
            with self.subTest(forbidden=forbidden):
                env = self.base()
                env[forbidden] = "should-not-be-here"
                with self.assertRaises(RuntimeError):
                    prepare_render_demo_environment(env)

    def test_conflicting_encryption_key_rejected(self):
        env = self.base()
        env["POTIGUAR_ONBOARDING_FERNET_KEY"] = "not-the-derived-key"
        with self.assertRaisesRegex(RuntimeError, "Conflicting"):
            prepare_render_demo_environment(env)

    def test_do_not_mutate_real_process_environ_in_tests(self):
        env = self.base()
        with patch.dict("os.environ", {}, clear=True):
            prepare_render_demo_environment(env)
            self.assertIsNotNone(env.get("POTIGUAR_ONBOARDING_FERNET_KEY"))
