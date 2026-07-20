from app.models import User


def test_password_hash_column_supports_default_werkzeug_hash():
    user = User(username="admin-capacidade")
    user.set_password("senha-segura-sintetica-123")

    column_length = User.__table__.c.password_hash.type.length

    assert len(user.password_hash) > 128
    assert column_length is not None
    assert column_length >= len(user.password_hash)
    assert user.check_password("senha-segura-sintetica-123")
