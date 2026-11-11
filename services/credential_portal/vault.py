"""Cofre local: API key cifrada com Fernet em SQLite, chave mestra fora do banco.

Não publica credenciais nem registra seu conteúdo. O diretório privado
permanece fora do Git e só pode ser lido pela conta de serviço.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


class CredentialVaultError(RuntimeError):
    pass


def _private_root(directory: str | Path) -> Path:
    root = Path(directory).expanduser().resolve()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.stat().st_mode & 0o077:
        raise CredentialVaultError("diretório de credenciais permite acesso externo")
    return root


def _private_file(root: Path, name: str, generator) -> Path:
    path = root / name
    if not path.exists():
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(generator())
                    f.flush()
                    os.fsync(f.fileno())
            except Exception:
                path.unlink(missing_ok=True)
                raise
    if path.stat().st_mode & 0o077:
        raise CredentialVaultError("arquivo privado possui permissões excessivas")
    return path


def _fernet(root: Path) -> Fernet:
    master = _private_file(root, "vault-fernet.key", Fernet.generate_key)
    return Fernet(master.read_bytes())


def _db(root: Path):
    db_path = root / "credentials.sqlite3"
    if db_path.exists() and db_path.stat().st_mode & 0o077:
        raise CredentialVaultError("SQLite possui permissões excessivas")
    conn = sqlite3.connect(str(db_path), timeout=5)
    os.chmod(db_path, 0o600)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
          provider TEXT PRIMARY KEY,
          ciphertext BLOB NOT NULL,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn


def store_gemini_api_key(directory: str | Path, key: str) -> None:
    if not isinstance(key, str) or not 20 <= len(key) <= 512:
        raise CredentialVaultError("formato de chave inválido")
    if any(c.isspace() for c in key) or not key.isprintable():
        raise CredentialVaultError("chave contém caracteres inválidos")
    root = _private_root(directory)
    ciphertext = _fernet(root).encrypt(key.encode("utf-8"))
    with _db(root) as connection:
        connection.execute(
            """INSERT INTO credentials(provider, ciphertext) VALUES (?, ?)
               ON CONFLICT(provider) DO UPDATE SET
               ciphertext=excluded.ciphertext, updated_at=CURRENT_TIMESTAMP""",
            ("gemini", ciphertext),
        )


def load_gemini_api_key(directory: str | Path) -> str | None:
    root = Path(directory).expanduser().resolve()
    if not root.exists():
        return None
    root = _private_root(root)
    db_path = root / "credentials.sqlite3"
    master = root / "vault-fernet.key"
    if not db_path.exists() or not master.exists():
        return None
    if db_path.stat().st_mode & 0o077 or master.stat().st_mode & 0o077:
        raise CredentialVaultError("cofre não está com permissões privadas")
    with _db(root) as connection:
        row = connection.execute(
            "SELECT ciphertext FROM credentials WHERE provider=?", ("gemini",)
        ).fetchone()
    if not row:
        return None
    try:
        return Fernet(master.read_bytes()).decrypt(row[0]).decode("utf-8")
    except (InvalidToken, UnicodeError, ValueError) as exc:
        raise CredentialVaultError("não foi possível abrir o cofre") from exc
