"""Basic route tests for Smart Energy Platform."""

import os
import pytest

# Minimal env for import without real Supabase
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test")
os.environ.setdefault("SECRET_KEY", "test-secret")

from dbms import app


@pytest.fixture
def client():
    return app.test_client()


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200


def test_login_page(client):
    r = client.get("/login")
    assert r.status_code == 200


def test_register_page(client):
    r = client.get("/register")
    assert r.status_code == 200


def test_admin_map_reports_redirects_when_not_logged_in(client):
    r = client.get("/admin/map/reports")
    assert r.status_code == 302
    assert "/login" in (r.headers.get("Location") or "")


def test_admin_map_reports_export_redirects_when_not_logged_in(client):
    r = client.get("/admin/map/reports/export")
    assert r.status_code == 302
    assert "/login" in (r.headers.get("Location") or "")


def test_api_power_reports(client):
    r = client.get("/api/map/power-reports")
    assert r.status_code in (200, 500)  # 500 if Supabase not configured
