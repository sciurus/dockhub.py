from click.testing import CliRunner

from dockhub import main, DOCKERHUB_URL


def test_basic():
    """Verify that it runs and spits out help."""
    runner = CliRunner()
    result = runner.invoke(main, "--help")
    assert result.exit_code == 0


def test_missing_dh_username(monkeypatch):
    """Verify missing DH_USERNAME kicks up error."""
    monkeypatch.setenv("DH_USERNAME", "")
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 1
    # Assert that a substring of the error message is in the output
    assert "variable DH_USERNAME" in result.output


def test_missing_dh_password(monkeypatch):
    """Verify missing DH_PASSWORD kicks up error."""
    monkeypatch.setenv("DH_USERNAME", "test")
    monkeypatch.setenv("DH_PASSWORD", "")
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 1
    # Assert that a substring of the error message is in the output
    assert "variable DH_PASSWORD" in result.output


def test_good_auth(monkeypatch, requests_mock):
    """Verify auth works."""
    requests_mock.post(f"{DOCKERHUB_URL}/users/login/", json={"token": "t"})
    monkeypatch.setenv("DH_USERNAME", "testuser")
    monkeypatch.setenv("DH_PASSWORD", "testpass")

    runner = CliRunner()
    result = runner.invoke(main)
    # This defaults to --action=list which in this case does nothing
    assert result.exit_code == 0
    assert result.output == ""
