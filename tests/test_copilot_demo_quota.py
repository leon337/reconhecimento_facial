"""Limite compartilhado de sessões de demonstração."""
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.copilot.demo_quota import DemoQuotaReached, reserve_session


def test_quota_is_persistent_and_atomic(tmp_path):
    def request(_):
        try:
            reserve_session(str(tmp_path), 5)
            return True
        except DemoQuotaReached:
            return False

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(request, range(30)))
    assert results.count(True) == 5
    assert results.count(False) == 25
    with pytest.raises(DemoQuotaReached):
        reserve_session(str(tmp_path), 5)


def test_quota_is_opt_in(tmp_path):
    assert reserve_session(str(tmp_path), 0) == 0
    assert not (tmp_path / "copilot-demo-quota.sqlite3").exists()
