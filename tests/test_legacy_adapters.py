import pytest

from app.infrastructure.legacy import (
    LegacySqlAlchemyUnitOfWork,
    LegacyUserRepository,
)
from app.models import User, db


def test_legacy_user_repository_add_get_and_list(app):
    with app.app_context():
        repository = LegacyUserRepository()
        user = User(username="sintetico", role="funcionario")
        user.set_password("senha-sintetica")

        repository.add(user)
        db.session.commit()

        loaded = repository.get(user.id)
        listed = list(repository.list(username="sintetico"))

        assert loaded is not None
        assert loaded.username == "sintetico"
        assert [item.id for item in listed] == [user.id]


def test_legacy_user_repository_rejects_unknown_filter(app):
    with app.app_context():
        repository = LegacyUserRepository()

        with pytest.raises(ValueError, match="não suportados"):
            list(repository.list(tenant_id="empresa-inexistente"))


def test_legacy_unit_of_work_commits_and_rolls_back(app):
    with app.app_context():
        uow = LegacySqlAlchemyUnitOfWork()
        user = User(username="commit-sintetico", role="funcionario")
        user.set_password("senha-sintetica")

        with uow:
            db.session.add(user)
            uow.commit()

        assert User.query.filter_by(username="commit-sintetico").one_or_none() is not None

        with pytest.raises(RuntimeError):
            with uow:
                transient = User(username="rollback-sintetico", role="funcionario")
                transient.set_password("senha-sintetica")
                db.session.add(transient)
                raise RuntimeError("forçar rollback")

        assert User.query.filter_by(username="rollback-sintetico").one_or_none() is None
