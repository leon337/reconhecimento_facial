"""A URL base do sistema deve encaminhar à área administrativa."""

def test_home_redirects_to_login(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/admin/login"

def test_home_login_is_rendered(client):
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login administrativo" in response.data
