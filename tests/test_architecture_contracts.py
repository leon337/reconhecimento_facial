from datetime import datetime, timezone

from app.application.contracts import AuditSink, Clock, ObjectStorage, SecretBox


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


class MemoryStorage:
    def __init__(self):
        self.items = {}

    def save_private(self, *, content: bytes, media_type: str) -> str:
        key = f"item-{len(self.items) + 1}"
        self.items[key] = (content, media_type)
        return key

    def read_private(self, key: str) -> bytes:
        return self.items[key][0]

    def delete_private(self, key: str) -> None:
        del self.items[key]


class ReversibleSecretBox:
    def encrypt(self, plaintext: bytes, *, context: bytes = b"") -> bytes:
        return context + b":" + plaintext[::-1]

    def decrypt(self, ciphertext: bytes, *, context: bytes = b"") -> bytes:
        prefix = context + b":"
        assert ciphertext.startswith(prefix)
        return ciphertext[len(prefix):][::-1]


class MemoryAuditSink:
    def __init__(self):
        self.events = []

    def record(self, **event) -> None:
        self.events.append(event)


def test_clock_contract_accepts_timezone_aware_implementation():
    clock = FixedClock()

    assert isinstance(clock, Clock)
    assert clock.now().utcoffset() is not None


def test_private_storage_contract_supports_lifecycle():
    storage = MemoryStorage()

    assert isinstance(storage, ObjectStorage)
    key = storage.save_private(content=b"foto-sintetica", media_type="image/jpeg")
    assert storage.read_private(key) == b"foto-sintetica"
    storage.delete_private(key)
    assert key not in storage.items


def test_secret_box_contract_round_trip():
    secret_box = ReversibleSecretBox()

    assert isinstance(secret_box, SecretBox)
    encrypted = secret_box.encrypt(b"encoding-sintetico", context=b"tenant-1")
    assert encrypted != b"encoding-sintetico"
    assert secret_box.decrypt(encrypted, context=b"tenant-1") == b"encoding-sintetico"


def test_audit_contract_records_metadata_without_biometric_payload():
    audit = MemoryAuditSink()

    assert isinstance(audit, AuditSink)
    audit.record(
        action="BIOMETRIC_ENROLLED",
        actor_id="admin-1",
        tenant_id="tenant-1",
        subject_id="employee-1",
        occurred_at=datetime.now(timezone.utc),
        metadata={"sample_count": 1},
    )

    assert audit.events[0]["action"] == "BIOMETRIC_ENROLLED"
    assert "encoding" not in audit.events[0]["metadata"]
