"""
Report Sharing Service
Allow users to generate shareable links for their lab reports
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid

logger = logging.getLogger(__name__)


class SharedReport(Base):
    """Model for shared report links"""
    __tablename__ = "shared_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    share_token = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    access_count = Column(Integer, default=0)
    max_access_count = Column(Integer, nullable=True)  # Optional access limit
    password_hash = Column(String(255), nullable=True)  # Optional password protection
    

class SharingService:
    """Service for managing report sharing"""
    
    @staticmethod
    def create_share_link(
        db: Session,
        report_id: uuid.UUID,
        expires_in_days: int = 7,
        max_access: Optional[int] = None,
        password: Optional[str] = None
    ) -> str:
        """
        Create a shareable link for a report
        
        Args:
            db: Database session
            report_id: UUID of report to share
            expires_in_days: Days until link expires (default 7)
            max_access: Maximum number of times link can be accessed
            password: Optional password for protection
            
        Returns:
            Share token (URL-safe string)
        """
        # Generate secure token
        share_token = secrets.token_urlsafe(32)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Hash password if provided
        password_hash = None
        if password:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            password_hash = pwd_context.hash(password)
        
        # Create share record
        shared_report = SharedReport(
            report_id=report_id,
            share_token=share_token,
            expires_at=expires_at,
            max_access_count=max_access,
            password_hash=password_hash
        )
        
        db.add(shared_report)
        db.commit()
        db.refresh(shared_report)
        
        logger.info(f"Created share link for report {report_id}, expires {expires_at}")
        
        return share_token
    
    @staticmethod
    def get_shared_report(
        db: Session,
        share_token: str,
        password: Optional[str] = None
    ) -> Optional[uuid.UUID]:
        """
        Get report ID from share token and validate access
        
        Args:
            db: Database session
            share_token: The share token
            password: Optional password if link is protected
            
        Returns:
            Report UUID if valid, None if invalid/expired
        """
        from sqlalchemy import and_
        
        # Find share record
        shared = db.query(SharedReport).filter(
            and_(
                SharedReport.share_token == share_token,
                SharedReport.is_active == True
            )
        ).first()
        
        if not shared:
            logger.warning(f"Share token not found or inactive: {share_token[:10]}...")
            return None
        
        # Check expiration
        if shared.expires_at and datetime.utcnow() > shared.expires_at:
            logger.warning(f"Share link expired: {share_token[:10]}...")
            return None
        
        # Check access count
        if shared.max_access_count and shared.access_count >= shared.max_access_count:
            logger.warning(f"Share link access limit reached: {share_token[:10]}...")
            return None
        
        # Check password if required
        if shared.password_hash and password:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            if not pwd_context.verify(password, shared.password_hash):
                logger.warning(f"Invalid password for share link: {share_token[:10]}...")
                return None
        elif shared.password_hash and not password:
            logger.warning(f"Password required for share link: {share_token[:10]}...")
            return None
        
        # Increment access count
        shared.access_count += 1
        db.commit()
        
        logger.info(f"Share link accessed: {share_token[:10]}... (count: {shared.access_count})")
        
        return shared.report_id
    
    @staticmethod
    def revoke_share_link(db: Session, share_token: str) -> bool:
        """
        Revoke a share link
        
        Args:
            db: Database session
            share_token: The share token to revoke
            
        Returns:
            True if revoked, False if not found
        """
        shared = db.query(SharedReport).filter(
            SharedReport.share_token == share_token
        ).first()
        
        if not shared:
            return False
        
        shared.is_active = False
        db.commit()
        
        logger.info(f"Revoked share link: {share_token[:10]}...")
        return True
    
    @staticmethod
    def list_active_shares(db: Session, report_id: uuid.UUID) -> list:
        """
        List all active share links for a report
        
        Args:
            db: Database session
            report_id: Report UUID
            
        Returns:
            List of share records
        """
        from sqlalchemy import and_
        
        shares = db.query(SharedReport).filter(
            and_(
                SharedReport.report_id == report_id,
                SharedReport.is_active == True
            )
        ).all()
        
        return shares
    
    @staticmethod
    def get_share_analytics(db: Session, share_token: str) -> dict:
        """
        Get analytics for a share link
        
        Args:
            db: Database session
            share_token: The share token
            
        Returns:
            Dict with analytics data
        """
        shared = db.query(SharedReport).filter(
            SharedReport.share_token == share_token
        ).first()
        
        if not shared:
            return {}
        
        return {
            "token": share_token,
            "created_at": shared.created_at,
            "expires_at": shared.expires_at,
            "access_count": shared.access_count,
            "max_access_count": shared.max_access_count,
            "is_active": shared.is_active,
            "is_password_protected": bool(shared.password_hash)
        }


# Helper to create database table
def create_shared_reports_table(db: Session):
    """Create shared_reports table if it doesn't exist"""
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
