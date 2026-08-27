import uuid
from datetime import date, datetime
from typing import Any, Optional
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pfcompass.database import Base


class Citizen(Base):
    __tablename__ = "citizens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    auth_credential: Mapped[Optional["AuthCredential"]] = relationship("AuthCredential", back_populates="citizen", uselist=False)
    uan_records: Mapped[list["UANRecord"]] = relationship("UANRecord", back_populates="citizen")
    employment_histories: Mapped[list["EmploymentHistory"]] = relationship("EmploymentHistory", back_populates="citizen")
    health_findings: Mapped[list["HealthFinding"]] = relationship("HealthFinding", back_populates="citizen")
    claims: Mapped[list["Claim"]] = relationship("Claim", back_populates="citizen")
    cases: Mapped[list["Case"]] = relationship("Case", back_populates="citizen")


class AuthCredential(Base):
    __tablename__ = "auth_credentials"

    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citizens.id", ondelete="CASCADE"), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    citizen: Mapped["Citizen"] = relationship("Citizen", back_populates="auth_credential")


class UANRecord(Base):
    __tablename__ = "uan_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    uan: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    kyc_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    citizen: Mapped["Citizen"] = relationship("Citizen", back_populates="uan_records")
    employment_histories: Mapped[list["EmploymentHistory"]] = relationship("EmploymentHistory", back_populates="uan_record")


class EmploymentHistory(Base):
    __tablename__ = "employment_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    uan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uan_records.id"), nullable=False, index=True)
    employer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employer_establishment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=False)
    date_of_exit: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    exit_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    basic_wage_history: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    is_data_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_source: Mapped[str] = mapped_column(String(50), default="DEMO_SEED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    citizen: Mapped["Citizen"] = relationship("Citizen", back_populates="employment_histories")
    uan_record: Mapped["UANRecord"] = relationship("UANRecord", back_populates="employment_histories")
    pf_accounts: Mapped[list["PFAccount"]] = relationship("PFAccount", back_populates="employment_history")


class PFAccount(Base):
    __tablename__ = "pf_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employment_history.id"), nullable=False, index=True)
    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    member_id: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), default="EPF", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False, index=True)
    inoperative_since: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employment_history: Mapped["EmploymentHistory"] = relationship("EmploymentHistory", back_populates="pf_accounts")
    balance_snapshots: Mapped[list["PFBalanceSnapshot"]] = relationship("PFBalanceSnapshot", back_populates="pf_account")


class PFBalanceSnapshot(Base):
    __tablename__ = "pf_balance_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pf_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pf_accounts.id"), nullable=False, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    employee_share: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    employer_share: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    interest_accrued: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_balance: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    data_source: Mapped[str] = mapped_column(String(50), default="DEMO_SEED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pf_account: Mapped["PFAccount"] = relationship("PFAccount", back_populates="balance_snapshots")


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    yaml_definition: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    source_reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), default="SYSTEM", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HealthFinding(Base):
    __tablename__ = "health_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    pf_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("pf_accounts.id"), nullable=True)
    employment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("employment_history.id"), nullable=True)
    rule_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rule_versions.id"), nullable=False)
    rule_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False, index=True)
    what_is_wrong: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_happened: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    potential_impact: Mapped[str] = mapped_column(Text, nullable=False)
    correction_path: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    case_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    citizen: Mapped["Citizen"] = relationship("Citizen", back_populates="health_findings")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    claim_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    intent_source: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_intent_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False, index=True)
    eligibility_result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    calculation_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    presubmit_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    citizen: Mapped["Citizen"] = relationship("Citizen", back_populates="claims")
    cases: Mapped[list["Case"]] = relationship("Case", back_populates="claim")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    case_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    case_subtype: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False, index=True)
    claim_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=True)
    finding_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("health_findings.id"), nullable=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    citizen: Mapped["Citizen"] = relationship("Citizen", back_populates="cases")
    claim: Mapped[Optional["Claim"]] = relationship("Claim", back_populates="cases")
    events: Mapped[list["CaseEvent"]] = relationship("CaseEvent", back_populates="case", order_by="CaseEvent.occurred_at.asc()")


class CaseEvent(Base):
    __tablename__ = "case_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(50), nullable=False)
    what_happened: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_happened: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metadata_payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case: Mapped["Case"] = relationship("Case", back_populates="events")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    citizen_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    ip_address_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)
    detail: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
