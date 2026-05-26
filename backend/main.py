"""
Main FastAPI application for MediScan AI – Smart Medical Report Interpreter
"""
import os
import logging
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, UUID4
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import models
from database import engine, get_db, Base, SessionLocal
from config import get_settings
import ocr_service
import parser_service
import explanation_service
import auth

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

# ── Database ─────────────────────────────────────────────────────────────────
# Ensure all tables exist (incl. SharedReport from sharing_service)
import sharing_service  # registers SharedReport model before create_all
Base.metadata.create_all(bind=engine)

# ── App setup ────────────────────────────────────────────────────────────────
settings = get_settings()
app = FastAPI(
    title="MediScan AI",
    version="2.0.0",
    description="AI-powered medical lab report interpreter with OCR and structured result parsing",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class ReportStatus(BaseModel):
    id: UUID4
    status: str
    error_message: Optional[str] = None


class LabResultResponse(BaseModel):
    id: UUID4
    test_name: str
    canonical_name: str
    value_numeric: Optional[float]
    value_text: str
    unit: Optional[str]
    ref_low: Optional[float]
    ref_high: Optional[float]
    ref_text: Optional[str]
    status: str

    class Config:
        from_attributes = True


class ExplanationResponse(BaseModel):
    summary: str
    tips: str
    disclaimer: str

    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    id: UUID4
    status: str
    report_type: Optional[str]
    title: Optional[str]
    notes: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    lab_results: List[LabResultResponse]
    explanation: Optional[ExplanationResponse]

    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    id: UUID4
    status: str
    report_type: Optional[str]
    title: Optional[str]
    notes: Optional[str]
    created_at: datetime
    result_count: int

    class Config:
        from_attributes = True


class ReportUpdateRequest(BaseModel):
    report_type: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None


# ── Background processing ─────────────────────────────────────────────────────

def process_report(report_id: str, file_path: str, save_report: bool):
    """
    Background task to process a medical report.
    Creates its own DB session to avoid sharing a closed request-scoped session.
    """
    db = SessionLocal()
    try:
        logger.info(f"[report:{report_id[:8]}] Processing started")

        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not report:
            logger.error(f"[report:{report_id[:8]}] Not found in database")
            return

        report.status = "processing"
        db.commit()

        _log_audit(db, report_id, "processing_started", "OCR and parsing initiated")

        # Step 1 – OCR
        extracted_text, confidence, ocr_engine = ocr_service.extract_text_from_file(file_path)

        if not extracted_text or len(extracted_text.strip()) < 20:
            raise ValueError("No meaningful text could be extracted from the uploaded file. "
                             "Please ensure the file is clear and contains lab results.")

        logger.info(f"[report:{report_id[:8]}] OCR: {len(extracted_text)} chars, "
                    f"confidence={confidence:.2f}, engine={ocr_engine}")

        if save_report:
            db.add(models.ExtractedText(
                report_id=report_id,
                text=extracted_text,
                ocr_engine=ocr_engine,
                confidence=confidence,
            ))
            db.commit()

        # Step 2 – Parse
        parsed_results = parser_service.parse_lab_results(extracted_text)

        if not parsed_results:
            logger.warning(f"[report:{report_id[:8]}] No lab results parsed – saving as empty report")

        for parsed in parsed_results:
            db.add(models.LabResult(
                report_id=report_id,
                test_name=parsed.test_name,
                canonical_name=parsed.canonical_name,
                value_numeric=parsed.value_numeric,
                value_text=parsed.value_text,
                unit=parsed.unit,
                ref_low=parsed.ref_low,
                ref_high=parsed.ref_high,
                ref_text=parsed.ref_text,
                status=parsed.status,
            ))

        db.commit()
        logger.info(f"[report:{report_id[:8]}] Saved {len(parsed_results)} lab results")

        # Step 3 – Detect report type
        report_type = parser_service.detect_report_type(parsed_results)
        report.report_type = report_type

        # Step 4 – Generate explanation
        explanation_data = _generate_explanation(parsed_results, report_type, report_id)

        db.add(models.Explanation(
            report_id=report_id,
            summary=explanation_data["summary"],
            tips=explanation_data["tips"],
            disclaimer=explanation_data["disclaimer"],
        ))

        report.status = "done"
        report.processed_at = datetime.utcnow()
        db.commit()

        _log_audit(db, report_id, "processing_completed",
                   f"Successfully processed {len(parsed_results)} results")
        logger.info(f"[report:{report_id[:8]}] Done – {report_type}")

        # Clean up file if not saving
        if not save_report and settings.DELETE_FILES_AFTER_PROCESSING:
            _safe_delete_file(file_path)

    except Exception as e:
        logger.error(f"[report:{report_id[:8]}] Processing failed: {e}", exc_info=True)
        try:
            report = db.query(models.Report).filter(models.Report.id == report_id).first()
            if report:
                report.status = "failed"
                report.error_message = str(e)
                report.processed_at = datetime.utcnow()
                db.commit()
            _log_audit(db, report_id, "processing_failed", f"Error: {str(e)}")
        except Exception as db_err:
            logger.error(f"[report:{report_id[:8]}] Failed to record error: {db_err}")
    finally:
        db.close()


def _generate_explanation(parsed_results, report_type: str, report_id: str) -> dict:
    """Try AI explanation, fall back to rule-based."""
    if os.getenv("ENABLE_AI_EXPLANATIONS", "false").lower() == "true":
        try:
            import ai_service
            ai_svc = ai_service.get_ai_service()
            data = ai_svc.generate_personalized_explanation(
                results=parsed_results,
                report_type=report_type,
            )
            logger.info(f"[report:{report_id[:8]}] AI explanation generated")
            return data
        except Exception as e:
            logger.warning(f"[report:{report_id[:8]}] AI failed, using fallback: {e}")
    return explanation_service.generate_explanation(parsed_results, report_type)


def _log_audit(db: Session, report_id: str, action: str, message: str):
    try:
        db.add(models.AuditLog(report_id=report_id, action=action, message=message))
        db.commit()
    except Exception as e:
        logger.warning(f"Audit log failed: {e}")


def _safe_delete_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted upload file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not delete file {file_path}: {e}")


# ── Helper: build ReportResponse ──────────────────────────────────────────────

def _build_report_response(report, db: Session) -> ReportResponse:
    lab_results = db.query(models.LabResult).filter(
        models.LabResult.report_id == report.id
    ).all()

    explanation = db.query(models.Explanation).filter(
        models.Explanation.report_id == report.id
    ).first()

    exp_response = None
    if explanation:
        exp_response = ExplanationResponse(
            summary=explanation.summary or "",
            tips=explanation.tips or "",
            disclaimer=explanation.disclaimer or "",
        )

    return ReportResponse(
        id=report.id,
        status=report.status,
        report_type=report.report_type,
        title=report.title,
        notes=report.notes,
        created_at=report.created_at,
        processed_at=report.processed_at,
        lab_results=[LabResultResponse.from_orm(lr) for lr in lab_results],
        explanation=exp_response,
    )


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring and Docker."""
    db_status = "ok"
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "app": "MediScan AI",
        "version": "2.0.0",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    return {"app": "MediScan AI", "version": "2.0.0", "status": "running", "docs": "/docs"}


# ── Auth endpoints ────────────────────────────────────────────────────────────

@app.post("/api/auth/register", response_model=auth.UserResponse)
async def register(user_data: auth.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    if "@" not in user_data.email or "." not in user_data.email:
        raise HTTPException(400, "Invalid email format")

    if len(user_data.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    try:
        user = auth.create_user(db, user_data.email, user_data.password)
        logger.info(f"New user registered: {user.email}")
        return auth.UserResponse.from_orm(user)
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(500, "Registration failed")


@app.post("/api/auth/login", response_model=auth.Token)
async def login(user_data: auth.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(401, "Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token = auth.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    logger.info(f"User logged in: {user.email}")
    return auth.Token(access_token=access_token, token_type="bearer")


@app.get("/api/auth/me", response_model=auth.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_user_required)):
    return auth.UserResponse.from_orm(current_user)


# ── Report endpoints ──────────────────────────────────────────────────────────

@app.post("/api/reports/upload", response_model=ReportStatus)
async def upload_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    save_report: bool = Form(default=False),
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a medical report (image or PDF) for OCR + AI processing."""
    try:
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(400, "Uploaded file is empty")

        if len(content) > settings.MAX_FILE_SIZE:
            max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
            raise HTTPException(413, f"File too large. Maximum allowed size is {max_mb} MB")

        file_ext = Path(file.filename or "").suffix.lower()
        if not file_ext:
            raise HTTPException(400, "File has no extension. Please upload a JPG, PNG, or PDF file")

        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                400,
                f"File type '{file_ext}' is not supported. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}",
            )

        # Sanitise filename
        safe_name = Path(file.filename).stem[:50] if file.filename else "report"
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in "-_")

        report = models.Report(
            status="queued",
            save_report=save_report,
            user_id=current_user.id if current_user else None,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        report_id = str(report.id)
        logger.info(
            f"[report:{report_id[:8]}] Created" +
            (f" for user {current_user.email}" if current_user else " (anonymous)")
        )

        file_path = os.path.join(settings.UPLOAD_DIR, f"{report_id}{file_ext}")
        with open(file_path, "wb") as f:
            f.write(content)

        db.add(models.ReportFile(
            report_id=report.id,
            file_name=file.filename or f"report{file_ext}",
            storage_path=file_path,
            mime_type=file.content_type,
            file_size=len(content),
        ))
        db.commit()

        background_tasks.add_task(process_report, report_id, file_path, save_report)

        return ReportStatus(id=report.id, status="queued")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(500, "Upload failed. Please try again.")


@app.get("/api/reports/{report_id}/status", response_model=ReportStatus)
async def get_report_status(
    report_id: UUID4,
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    if report.user_id and current_user and report.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    return ReportStatus(id=report.id, status=report.status, error_message=report.error_message)


@app.get("/api/reports", response_model=List[ReportListItem])
async def list_reports(
    limit: int = 20,
    offset: int = 0,
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """List reports. Authenticated users see their own; anonymous sees anonymous."""
    query = db.query(models.Report)

    if current_user:
        query = query.filter(models.Report.user_id == current_user.id)
    else:
        query = query.filter(models.Report.user_id == None)

    reports = query.order_by(models.Report.created_at.desc()).limit(limit).offset(offset).all()

    result = []
    for r in reports:
        count = db.query(models.LabResult).filter(models.LabResult.report_id == r.id).count()
        result.append(ReportListItem(
            id=r.id,
            status=r.status,
            report_type=r.report_type,
            title=r.title,
            notes=r.notes,
            created_at=r.created_at,
            result_count=count,
        ))
    return result


@app.get("/api/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID4,
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Get full report details including lab results and explanation."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    if report.user_id and current_user and report.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    return _build_report_response(report, db)


@app.post("/api/reports/demo", response_model=ReportResponse)
async def create_demo_report(
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Create a demo report using built-in sample data (no file upload needed)."""
    sample_text = """
    LABORATORY REPORT

    Complete Blood Count (CBC)

    White Blood Cells (WBC): 7.2 x10^3/uL (4.0-11.0)
    Red Blood Cells (RBC): 4.8 x10^6/uL (4.2-5.9)
    Hemoglobin: 14.2 g/dL (12.0-16.0)
    Hematocrit: 42.5 % (36.0-48.0)
    Platelets: 245 x10^3/uL (150-400)

    Lipid Panel

    Total Cholesterol: 215 mg/dL (<200)
    LDL Cholesterol: 140 mg/dL (<100)
    HDL Cholesterol: 52 mg/dL (>40)
    Triglycerides: 148 mg/dL (<150)

    Metabolic Panel

    Glucose: 104 mg/dL (70-99)
    HbA1c: 5.6 % (<5.7)
    """

    try:
        report = models.Report(
            status="processing",
            save_report=False,
            user_id=current_user.id if current_user else None,
            title="Demo Lab Report",
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        parsed_results = parser_service.parse_lab_results(sample_text)

        for parsed in parsed_results:
            db.add(models.LabResult(
                report_id=report.id,
                test_name=parsed.test_name,
                canonical_name=parsed.canonical_name,
                value_numeric=parsed.value_numeric,
                value_text=parsed.value_text,
                unit=parsed.unit,
                ref_low=parsed.ref_low,
                ref_high=parsed.ref_high,
                ref_text=parsed.ref_text,
                status=parsed.status,
            ))

        db.commit()

        report_type = parser_service.detect_report_type(parsed_results)
        report.report_type = report_type

        explanation_data = _generate_explanation(parsed_results, report_type, str(report.id))

        db.add(models.Explanation(
            report_id=report.id,
            summary=explanation_data["summary"],
            tips=explanation_data["tips"],
            disclaimer=explanation_data["disclaimer"],
        ))

        report.status = "done"
        report.processed_at = datetime.utcnow()
        db.commit()

        return _build_report_response(report, db)

    except Exception as e:
        logger.error(f"Demo report creation failed: {e}", exc_info=True)
        raise HTTPException(500, "Failed to create demo report")


@app.put("/api/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID4,
    update_data: ReportUpdateRequest,
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Update report metadata (title, report type, notes)."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    if report.user_id and current_user and report.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    if update_data.report_type is not None:
        report.report_type = update_data.report_type
    if update_data.title is not None:
        report.title = update_data.title
    if update_data.notes is not None:
        report.notes = update_data.notes

    db.commit()
    db.refresh(report)

    _log_audit(db, str(report_id), "report_updated", "Report metadata updated")

    return _build_report_response(report, db)


@app.delete("/api/reports/{report_id}")
async def delete_report(
    report_id: UUID4,
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a report and all associated data."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    if report.user_id and current_user and report.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    # Delete uploaded files
    for rf in db.query(models.ReportFile).filter(models.ReportFile.report_id == report_id).all():
        _safe_delete_file(rf.storage_path)

    db.delete(report)
    db.commit()

    logger.info(f"[report:{str(report_id)[:8]}] Deleted")
    return {"message": "Report deleted successfully"}


# ── PDF export ────────────────────────────────────────────────────────────────

@app.get("/api/reports/{report_id}/pdf")
async def export_report_pdf(
    report_id: UUID4,
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Export a completed report as a PDF file."""
    from fastapi.responses import StreamingResponse
    import pdf_generator

    try:
        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not report:
            raise HTTPException(404, "Report not found")

        if report.user_id and current_user and report.user_id != current_user.id:
            raise HTTPException(403, "Access denied")

        if report.status != "done":
            raise HTTPException(400, "Report has not finished processing yet")

        lab_results = db.query(models.LabResult).filter(
            models.LabResult.report_id == report_id
        ).all()

        if not lab_results:
            raise HTTPException(400, "No lab results found for this report")

        explanation = db.query(models.Explanation).filter(
            models.Explanation.report_id == report_id
        ).first()

        parsed_results = [
            parser_service.ParsedLabResult(
                test_name=lr.test_name,
                canonical_name=lr.canonical_name,
                value_numeric=lr.value_numeric,
                value_text=lr.value_text or "",
                unit=lr.unit,
                ref_low=lr.ref_low,
                ref_high=lr.ref_high,
                ref_text=lr.ref_text,
                status=lr.status,
            )
            for lr in lab_results
        ]

        explanation_data = {
            "summary": explanation.summary if explanation else "",
            "tips": explanation.tips if explanation else "",
            "disclaimer": explanation.disclaimer if explanation else "",
        }

        generator = pdf_generator.get_pdf_generator()
        pdf_buffer = generator.generate_report(
            results=parsed_results,
            explanation=explanation_data,
            report_id=str(report_id),
            report_type=report.report_type or "General Lab Report",
            patient_name=report.title,
            report_date=report.created_at,
        )

        safe_type = (report.report_type or "report").replace(" ", "_").replace("(", "").replace(")", "").lower()
        filename = f"mediscan_{safe_type}_{str(report_id)[:8]}.pdf"

        logger.info(f"[report:{str(report_id)[:8]}] PDF exported")

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF generation failed for report {report_id}: {e}", exc_info=True)
        raise HTTPException(500, "Failed to generate PDF report")


# ── Sharing endpoints ─────────────────────────────────────────────────────────

class ShareLinkCreate(BaseModel):
    expires_in_days: int = 7
    max_access: Optional[int] = None
    password: Optional[str] = None


class ShareLinkResponse(BaseModel):
    id: str
    share_token: str
    share_url: str
    expires_at: Optional[datetime]
    max_access: Optional[int]
    access_count: int
    is_password_protected: bool
    is_active: bool


@app.post("/api/reports/{report_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    report_id: UUID4,
    share_data: ShareLinkCreate,
    current_user: models.User = Depends(auth.get_current_user_required),
    db: Session = Depends(get_db),
):
    """Create a shareable link for a report (requires authentication)."""
    if share_data.expires_in_days < 1 or share_data.expires_in_days > 90:
        raise HTTPException(400, "Expiration must be between 1 and 90 days")

    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(403, "You can only share your own reports")

    if report.status != "done":
        raise HTTPException(400, "Can only share fully processed reports")

    share_token = sharing_service.SharingService.create_share_link(
        db=db,
        report_id=report.id,
        expires_in_days=share_data.expires_in_days,
        max_access=share_data.max_access,
        password=share_data.password,
    )

    # Get the created record to return full info
    shared = db.query(sharing_service.SharedReport).filter(
        sharing_service.SharedReport.share_token == share_token
    ).first()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    share_url = f"{frontend_url}/shared/{share_token}"

    logger.info(f"[report:{str(report_id)[:8]}] Share link created by {current_user.email}")

    return ShareLinkResponse(
        id=str(shared.id),
        share_token=share_token,
        share_url=share_url,
        expires_at=shared.expires_at,
        max_access=shared.max_access_count,
        access_count=shared.access_count,
        is_password_protected=bool(shared.password_hash),
        is_active=shared.is_active,
    )


@app.get("/api/reports/{report_id}/shares", response_model=List[ShareLinkResponse])
async def list_share_links(
    report_id: UUID4,
    current_user: models.User = Depends(auth.get_current_user_required),
    db: Session = Depends(get_db),
):
    """List all active share links for a report."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    shares = sharing_service.SharingService.list_active_shares(db, report.id)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    return [
        ShareLinkResponse(
            id=str(s.id),
            share_token=s.share_token,
            share_url=f"{frontend_url}/shared/{s.share_token}",
            expires_at=s.expires_at,
            max_access=s.max_access_count,
            access_count=s.access_count,
            is_password_protected=bool(s.password_hash),
            is_active=s.is_active,
        )
        for s in shares
    ]


@app.delete("/api/reports/{report_id}/share/{share_token}")
async def revoke_share_link(
    report_id: UUID4,
    share_token: str,
    current_user: models.User = Depends(auth.get_current_user_required),
    db: Session = Depends(get_db),
):
    """Revoke a share link."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    success = sharing_service.SharingService.revoke_share_link(db, share_token)
    if not success:
        raise HTTPException(404, "Share link not found")

    logger.info(f"[report:{str(report_id)[:8]}] Share link revoked by {current_user.email}")
    return {"message": "Share link revoked successfully"}


@app.get("/api/shared/{share_token}", response_model=ReportResponse)
async def access_shared_report(
    share_token: str,
    password: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Access a shared report via token (no authentication required)."""
    report_id = sharing_service.SharingService.get_shared_report(
        db=db, share_token=share_token, password=password
    )

    if not report_id:
        raise HTTPException(
            403,
            "This share link is invalid, expired, or has reached its access limit",
        )

    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    return _build_report_response(report, db)


# ── Historical trends ─────────────────────────────────────────────────────────

class HistoricalTrendResponse(BaseModel):
    test_name: str
    canonical_name: str
    data_points: List[Dict]
    trend: str  # increasing, decreasing, stable, insufficient_data


@app.get("/api/trends", response_model=List[Dict])
async def get_all_trends(
    current_user: models.User = Depends(auth.get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get an overview of all tracked tests across user's reports.
    Returns a list of unique test names that appear in ≥2 reports.
    """
    from sqlalchemy import and_, func as sqlfunc

    user_report_ids = [
        r.id for r in db.query(models.Report).filter(
            and_(models.Report.user_id == current_user.id, models.Report.status == "done")
        ).all()
    ]

    if not user_report_ids:
        return []

    # Find tests with ≥2 data points
    test_counts = (
        db.query(
            models.LabResult.canonical_name,
            sqlfunc.count(models.LabResult.id).label("count"),
        )
        .filter(models.LabResult.report_id.in_(user_report_ids))
        .group_by(models.LabResult.canonical_name)
        .having(sqlfunc.count(models.LabResult.id) >= 2)
        .all()
    )

    return [{"test_name": tc.canonical_name, "count": tc.count} for tc in test_counts]


@app.get("/api/trends/{test_name}", response_model=HistoricalTrendResponse)
async def get_historical_trends(
    test_name: str,
    current_user: models.User = Depends(auth.get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get historical trend for a specific lab test across all user's reports."""
    from sqlalchemy import and_, or_

    user_reports = db.query(models.Report).filter(
        and_(models.Report.user_id == current_user.id, models.Report.status == "done")
    ).all()

    if not user_reports:
        raise HTTPException(404, "No processed reports found")

    report_ids = [r.id for r in user_reports]

    lab_results = (
        db.query(models.LabResult)
        .filter(
            and_(
                models.LabResult.report_id.in_(report_ids),
                or_(
                    models.LabResult.test_name.ilike(f"%{test_name}%"),
                    models.LabResult.canonical_name.ilike(f"%{test_name}%"),
                ),
            )
        )
        .order_by(models.LabResult.created_at)
        .all()
    )

    if not lab_results:
        raise HTTPException(404, f"No results found for test: {test_name}")

    report_map = {r.id: r for r in user_reports}

    data_points = []
    for lr in lab_results:
        rpt = report_map.get(lr.report_id)
        data_points.append({
            "date": rpt.created_at.isoformat() if rpt else None,
            "value": lr.value_numeric if lr.value_numeric is not None else lr.value_text,
            "unit": lr.unit,
            "status": lr.status,
            "ref_range": lr.ref_text or (
                f"{lr.ref_low}-{lr.ref_high}" if lr.ref_low and lr.ref_high else None
            ),
            "report_id": str(lr.report_id),
        })

    # Calculate trend
    trend = "insufficient_data"
    numeric_values = [dp["value"] for dp in data_points if isinstance(dp["value"], (int, float))]
    if len(numeric_values) >= 2:
        change = ((numeric_values[-1] - numeric_values[0]) / numeric_values[0]) * 100
        if abs(change) < 5:
            trend = "stable"
        elif change > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

    return HistoricalTrendResponse(
        test_name=lab_results[0].test_name,
        canonical_name=lab_results[0].canonical_name or lab_results[0].test_name,
        data_points=data_points,
        trend=trend,
    )


# ── Stats endpoint for dashboard ──────────────────────────────────────────────

@app.get("/api/stats")
async def get_stats(
    current_user: Optional[models.User] = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregate stats for the dashboard."""
    from sqlalchemy import and_, func as sqlfunc

    query = db.query(models.Report)
    if current_user:
        query = query.filter(models.Report.user_id == current_user.id)
    else:
        query = query.filter(models.Report.user_id == None)

    total_reports = query.count()
    done_reports = query.filter(models.Report.status == "done").count()

    # Count statuses across all done reports for this user
    report_ids = [r.id for r in query.filter(models.Report.status == "done").all()]

    status_counts = {"normal": 0, "high": 0, "low": 0, "unknown": 0}
    if report_ids:
        rows = (
            db.query(models.LabResult.status, sqlfunc.count(models.LabResult.id))
            .filter(models.LabResult.report_id.in_(report_ids))
            .group_by(models.LabResult.status)
            .all()
        )
        for status, cnt in rows:
            if status in status_counts:
                status_counts[status] = cnt

    return {
        "total_reports": total_reports,
        "done_reports": done_reports,
        "result_counts": status_counts,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
