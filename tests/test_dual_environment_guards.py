from unittest.mock import patch
import pytest
from main import create_app

@pytest.mark.parametrize('deploy_role,app_env',[
    ('development','production'),('production','development'),
    ('invalid','development'),
])
def test_reject_mismatched_deployment_environment(deploy_role,app_env):
    with patch.dict('os.environ',{'POTIGUAR_DEPLOYMENT_ROLE':deploy_role,
                                  'APP_ENV':app_env,'SECRET_KEY':'unit-only'}):
        with pytest.raises(RuntimeError):
            create_app({'TESTING':True})

def test_reject_public_demo_in_production():
    with patch.dict('os.environ',{'POTIGUAR_DEPLOYMENT_ROLE':'production',
                                  'APP_ENV':'production',
                                  'POTIGUAR_PUBLIC_DEMO':'1',
                                  'SECRET_KEY':'unit-only'}):
        with pytest.raises(RuntimeError,match='anônima proibida'):
            create_app({'TESTING':True})
