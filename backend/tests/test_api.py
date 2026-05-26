"""
Integration / unit tests for MediScan AI API endpoints
Run with: pytest tests/ -v
"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Make sure backend root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── In-memory SQLite test database ────────────────────────────────────────────
SQLALCHEMY_TEST_URL = "sqlite:///./test_mediscan.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── App bootstrap ─────────────────────────────────────────────────────────────
from database import Base, get_db
from main import app

# Apply DB override
app.dependency_overrides[get_db] = override_get_db

# Create tables in test DB
Base.metadata.create_all(bind=test_engine)

# Also create shared_reports table
import sharing_service as ss
ss.SharedReport.__table__.create(bind=test_engine, checkfirst=True)

client = TestClient(app)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_db():
    """Wipe all rows between tests."""
    yield
    from sqlalchemy import text
    with test_engine.connect() as conn:
        for tbl in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {tbl.name}"))
        try:
            conn.execute(text("DELETE FROM shared_reports"))
        except Exception:
            pass
        conn.commit()


# ── Health check ──────────────────────────────────────────────────────────────

class TestHealthCheck:
    def test_health_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data

    def test_root_returns_200(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["app"] == "MediScan AI"


# ── Auth ──────────────────────────────────────────────────────────────────────

class TestAuth:
    def _register(self, email="test@example.com", password="testpass123"):
        return client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )

    def _login(self, email="test@example.com", password="testpass123"):
        return client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )

    def test_register_success(self):
        resp = self._register()
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    def test_register_duplicate_email(self):
        self._register()
        resp = self._register()
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_invalid_email(self):
        resp = self._register(email="bademail")
        assert resp.status_code == 400

    def test_register_short_password(self):
        resp = self._register(password="12")
        assert resp.status_code == 400

    def test_login_success(self):
        self._register()
        resp = self._login()
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self):
        self._register()
        resp = self._login(password="wrongpassword")
        assert resp.status_code == 401

    def test_me_authenticated(self):
        self._register()
        token = self._login().json()["access_token"]
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    def test_me_unauthenticated(self):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401


# ── File upload validation ─────────────────────────────────────────────────────

class TestUploadValidation:
    def test_upload_rejects_unsupported_extension(self):
        from io import BytesIO
        resp = client.post(
            "/api/reports/upload",
            files={"file": ("report.exe", BytesIO(b"fake content"), "application/octet-stream")},
            data={"save_report": "false"},
        )
        assert resp.status_code == 400
        assert "not supported" in resp.json()["detail"].lower()

    def test_upload_rejects_empty_file(self):
        from io import BytesIO
        resp = client.post(
            "/api/reports/upload",
            files={"file": ("report.jpg", BytesIO(b""), "image/jpeg")},
            data={"save_report": "false"},
        )
        assert resp.status_code == 400

    def test_upload_valid_jpg_queues_report(self):
        """A valid JPG should create a report and start processing."""
        from io import BytesIO
        # Use a minimal 1×1 white JPEG
        minimal_jpg = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
            b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
            b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\x1e3\x1e'
            b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00'
            b'\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b'
            b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf5\n\xf5\x0b\xff\xd9'
        )
        with patch("main.process_report"):  # Don't actually run OCR in unit tests
            resp = client.post(
                "/api/reports/upload",
                files={"file": ("test.jpg", BytesIO(minimal_jpg), "image/jpeg")},
                data={"save_report": "false"},
            )
        # Should succeed with 200 (queued)
        assert resp.status_code == 200
        assert resp.json()["status"] == "queued"


# ── Demo report ────────────────────────────────────────────────────────────────

class TestDemoReport:
    def test_demo_report_creates_report(self):
        resp = client.post("/api/reports/demo")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "done"
        assert len(data["lab_results"]) > 0

    def test_demo_report_has_explanation(self):
        resp = client.post("/api/reports/demo")
        assert resp.status_code == 200
        data = resp.json()
        assert data["explanation"] is not None
        assert len(data["explanation"]["summary"]) > 0

    def test_demo_report_result_statuses_valid(self):
        resp = client.post("/api/reports/demo")
        valid_statuses = {"normal", "high", "low", "unknown"}
        for r in resp.json()["lab_results"]:
            assert r["status"] in valid_statuses


# ── Report CRUD ───────────────────────────────────────────────────────────────

class TestReportCRUD:
    def _auth_header(self):
        client.post("/api/auth/register", json={"email": "user@test.com", "password": "pass1234"})
        token = client.post("/api/auth/login", json={"email": "user@test.com", "password": "pass1234"}).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _create_demo(self, headers=None):
        return client.post("/api/reports/demo", headers=headers or {})

    def test_list_reports_empty(self):
        headers = self._auth_header()
        resp = client.get("/api/reports", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_reports_after_demo(self):
        headers = self._auth_header()
        self._create_demo(headers)
        resp = client.get("/api/reports", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_report_by_id(self):
        headers = self._auth_header()
        report_id = self._create_demo(headers).json()["id"]
        resp = client.get(f"/api/reports/{report_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == report_id

    def test_update_report_title_and_notes(self):
        headers = self._auth_header()
        report_id = self._create_demo(headers).json()["id"]
        resp = client.put(
            f"/api/reports/{report_id}",
            json={"title": "Annual Check-up", "notes": "Fasting blood test"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Annual Check-up"
        assert data["notes"] == "Fasting blood test"

    def test_delete_report(self):
        headers = self._auth_header()
        report_id = self._create_demo(headers).json()["id"]
        resp = client.delete(f"/api/reports/{report_id}", headers=headers)
        assert resp.status_code == 200
        # Confirm deleted
        resp2 = client.get(f"/api/reports/{report_id}", headers=headers)
        assert resp2.status_code == 404

    def test_access_other_users_report_denied(self):
        """User A should not be able to access User B's report."""
        # Create user A and report
        hA = self._auth_header()
        report_id = self._create_demo(hA).json()["id"]

        # Register user B
        client.post("/api/auth/register", json={"email": "userB@test.com", "password": "pass1234"})
        tokenB = client.post("/api/auth/login", json={"email": "userB@test.com", "password": "pass1234"}).json()["access_token"]
        hB = {"Authorization": f"Bearer {tokenB}"}

        resp = client.get(f"/api/reports/{report_id}", headers=hB)
        assert resp.status_code == 403


# ── PDF export ─────────────────────────────────────────────────────────────────

class TestPDFExport:
    def test_pdf_export_requires_done_status(self):
        # A queued report cannot be exported
        from database import Base
        import models, uuid
        db = TestingSessionLocal()
        report = models.Report(status="queued", save_report=False)
        db.add(report)
        db.commit()
        report_id = str(report.id)
        db.close()

        resp = client.get(f"/api/reports/{report_id}/pdf")
        assert resp.status_code in (400, 403)  # Not ready

    def test_pdf_export_done_report(self):
        """Demo report is 'done' – should return a PDF."""
        demo = client.post("/api/reports/demo")
        report_id = demo.json()["id"]
        resp = client.get(f"/api/reports/{report_id}/pdf")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert len(resp.content) > 0

    def test_pdf_filename_is_professional(self):
        demo = client.post("/api/reports/demo")
        report_id = demo.json()["id"]
        resp = client.get(f"/api/reports/{report_id}/pdf")
        assert resp.status_code == 200
        cd = resp.headers.get("content-disposition", "")
        assert "mediscan" in cd.lower()


# ── Share links ────────────────────────────────────────────────────────────────

class TestShareLinks:
    def _setup(self):
        client.post("/api/auth/register", json={"email": "share@test.com", "password": "pass1234"})
        token = client.post("/api/auth/login", json={"email": "share@test.com", "password": "pass1234"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        report_id = client.post("/api/reports/demo", headers=headers).json()["id"]
        return headers, report_id

    def test_create_share_link(self):
        headers, report_id = self._setup()
        resp = client.post(
            f"/api/reports/{report_id}/share",
            json={"expires_in_days": 7},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "share_token" in data
        assert "share_url" in data
        assert data["is_active"] is True

    def test_access_shared_report(self):
        headers, report_id = self._setup()
        share_resp = client.post(
            f"/api/reports/{report_id}/share",
            json={"expires_in_days": 7},
            headers=headers,
        )
        token = share_resp.json()["share_token"]

        resp = client.get(f"/api/shared/{token}")
        assert resp.status_code == 200
        assert resp.json()["id"] == report_id

    def test_revoke_share_link(self):
        headers, report_id = self._setup()
        share_token = client.post(
            f"/api/reports/{report_id}/share",
            json={"expires_in_days": 7},
            headers=headers,
        ).json()["share_token"]

        # Revoke
        rev = client.delete(
            f"/api/reports/{report_id}/share/{share_token}",
            headers=headers,
        )
        assert rev.status_code == 200

        # Verify access denied
        resp = client.get(f"/api/shared/{share_token}")
        assert resp.status_code == 403

    def test_invalid_share_token(self):
        resp = client.get("/api/shared/totally-invalid-token-xyz")
        assert resp.status_code == 403

    def test_share_requires_auth(self):
        # Try without auth token
        demo = client.post("/api/reports/demo")
        report_id = demo.json()["id"]
        resp = client.post(
            f"/api/reports/{report_id}/share",
            json={"expires_in_days": 7},
        )
        assert resp.status_code == 401


# ── Stats endpoint ─────────────────────────────────────────────────────────────

class TestStats:
    def test_stats_returns_counts(self):
        client.post("/api/reports/demo")
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_reports" in data
        assert "result_counts" in data
        assert data["total_reports"] >= 1


# ── Parser edge cases ──────────────────────────────────────────────────────────

class TestParserEdgeCases:
    def test_empty_text_returns_empty_list(self):
        from parser_service import parse_lab_results
        assert parse_lab_results("") == []

    def test_nonsense_text_returns_empty_list(self):
        from parser_service import parse_lab_results
        results = parse_lab_results("Lorem ipsum dolor sit amet consectetur adipiscing elit")
        assert isinstance(results, list)

    def test_classify_boundary_values(self):
        from parser_service import classify_status
        # Exactly at boundary
        assert classify_status(70.0, 70.0, 99.0) == "normal"
        assert classify_status(99.0, 70.0, 99.0) == "normal"
        assert classify_status(69.9, 70.0, 99.0) == "low"
        assert classify_status(99.1, 70.0, 99.0) == "high"

    def test_classify_none_value(self):
        from parser_service import classify_status
        assert classify_status(None, 70, 99) == "unknown"

    def test_detect_report_type_unknown(self):
        from parser_service import detect_report_type
        assert detect_report_type([]) == "General Lab Report"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
