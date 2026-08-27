import asyncio
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.database import AsyncSessionLocal, Base, engine
from pfcompass.models import (
    AuthCredential,
    Case,
    CaseEvent,
    Citizen,
    EmploymentHistory,
    HealthFinding,
    PFAccount,
    PFBalanceSnapshot,
    RuleVersion,
    UANRecord,
)
from pfcompass.services.auth_service import hash_password


async def seed_demo_citizens() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(Citizen).where(Citizen.email == "multi@pfcompass.demo"))
        if result.scalar_one_or_none():
            print("Demo data already seeded. Skipping.")
            return

        print("Seeding synthetic demo citizens...")

        # Common password for demo accounts
        pwd_hash = hash_password("demo123456")

        # Create Rule Versions for seed findings
        rule_v1 = RuleVersion(
            id=uuid.uuid4(),
            rule_id="PFH-001",
            version="1.0.0",
            domain="HEALTH",
            title="Inoperative PF Account",
            description="Account inactive for >36 months",
            yaml_definition={"id": "PFH-001", "severity": "HIGH"},
            effective_from=date(2016, 9, 1),
            is_active=True
        )
        rule_v2 = RuleVersion(
            id=uuid.uuid4(),
            rule_id="PFH-002",
            version="1.0.0",
            domain="HEALTH",
            title="Missing Date of Exit",
            description="Exit date missing after leaving employer",
            yaml_definition={"id": "PFH-002", "severity": "HIGH"},
            effective_from=date(2018, 1, 1),
            is_active=True
        )
        session.add_all([rule_v1, rule_v2])
        await session.flush()

        # ----------------------------------------------------------------------
        # 1. Multi-Issue Citizen: Rajesh Kumar
        # ----------------------------------------------------------------------
        c1 = Citizen(
            id=uuid.uuid4(),
            display_name="Rajesh Kumar",
            email="multi@pfcompass.demo",
            is_demo=True,
            date_of_birth=date(1985, 4, 12)
        )
        session.add(c1)
        await session.flush()

        session.add(AuthCredential(citizen_id=c1.id, password_hash=pwd_hash))

        uan1 = UANRecord(id=uuid.uuid4(), citizen_id=c1.id, uan="100987654321", is_primary=True, kyc_status="VERIFIED")
        uan2 = UANRecord(id=uuid.uuid4(), citizen_id=c1.id, uan="100123456789", is_primary=False, kyc_status="UNVERIFIED")
        session.add_all([uan1, uan2])
        await session.flush()

        emp1 = EmploymentHistory(
            id=uuid.uuid4(),
            citizen_id=c1.id,
            uan_id=uan1.id,
            employer_name="Acme Tech Solutions Ltd",
            date_of_joining=date(2015, 6, 1),
            date_of_exit=date(2019, 8, 31),
            exit_reason="RESIGNATION",
            is_data_verified=True
        )
        emp2 = EmploymentHistory(
            id=uuid.uuid4(),
            citizen_id=c1.id,
            uan_id=uan2.id,
            employer_name="Global Systems India Corp",
            date_of_joining=date(2019, 9, 15),
            date_of_exit=None,
            is_data_verified=False
        )
        session.add_all([emp1, emp2])
        await session.flush()

        acc1 = PFAccount(id=uuid.uuid4(), citizen_id=c1.id, employment_id=emp1.id, member_id="MH/BAN/0012345/000/0000101", status="INOPERATIVE")
        acc2 = PFAccount(id=uuid.uuid4(), citizen_id=c1.id, employment_id=emp2.id, member_id="DL/CPM/0098765/000/0000202", status="ACTIVE")
        session.add_all([acc1, acc2])
        await session.flush()

        session.add_all([
            PFBalanceSnapshot(id=uuid.uuid4(), pf_account_id=acc1.id, snapshot_date=date(2019, 8, 30), employee_share=145000, employer_share=45000, interest_accrued=12000, total_balance=202000),
            PFBalanceSnapshot(id=uuid.uuid4(), pf_account_id=acc2.id, snapshot_date=date(2024, 7, 31), employee_share=280000, employer_share=88000, interest_accrued=24000, total_balance=392000)
        ])

        # Findings for Multi-issue citizen
        f1 = HealthFinding(
            id=uuid.uuid4(),
            citizen_id=c1.id,
            pf_account_id=acc1.id,
            employment_id=emp1.id,
            rule_version_id=rule_v1.id,
            rule_id="PFH-001",
            severity="HIGH",
            status="OPEN",
            what_is_wrong="Your previous PF account with Acme Tech Solutions has been inactive for over 36 months.",
            why_it_happened="No contributions or transfer request occurred after resignation in August 2019.",
            potential_impact="Interest accumulation stops after account becomes inoperative and withdrawal requires offline verification.",
            correction_path={"summary": "Initiate online PF transfer Form 13 to your current active UAN account.", "form_numbers": ["FORM-13"], "estimated_days": 15},
            evidence=[{"field": "status", "expected": "TRANSFERRED/SETTLED", "actual": "INOPERATIVE"}]
        )
        f2 = HealthFinding(
            id=uuid.uuid4(),
            citizen_id=c1.id,
            pf_account_id=acc2.id,
            employment_id=emp2.id,
            rule_version_id=rule_v2.id,
            rule_id="PFH-004",
            severity="CRITICAL",
            status="OPEN",
            what_is_wrong="Multiple active UANs detected linked to your profile.",
            why_it_happened="A new UAN was generated by your current employer instead of linking your existing UAN.",
            potential_impact="Consolidated service history is broken, delaying pension eligibility and tax-free threshold calculations.",
            correction_path={"summary": "Apply for UAN consolidation via EPFO Member Portal or Joint Declaration.", "form_numbers": ["UAN-MERGE"], "estimated_days": 30},
            evidence=[{"field": "uan_count", "expected": "1", "actual": "2"}]
        )
        session.add_all([f1, f2])

        # ----------------------------------------------------------------------
        # 2. Claim-Ready Citizen: Ananya Sharma
        # ----------------------------------------------------------------------
        c2 = Citizen(
            id=uuid.uuid4(),
            display_name="Ananya Sharma",
            email="healthy@pfcompass.demo",
            is_demo=True,
            date_of_birth=date(1992, 11, 20)
        )
        session.add(c2)
        await session.flush()

        session.add(AuthCredential(citizen_id=c2.id, password_hash=pwd_hash))

        uan3 = UANRecord(id=uuid.uuid4(), citizen_id=c2.id, uan="100555666777", is_primary=True, kyc_status="VERIFIED")
        session.add(uan3)
        await session.flush()

        emp3 = EmploymentHistory(
            id=uuid.uuid4(),
            citizen_id=c2.id,
            uan_id=uan3.id,
            employer_name="Innovate Financial Technologies",
            date_of_joining=date(2017, 3, 1),
            date_of_exit=None,
            is_data_verified=True
        )
        session.add(emp3)
        await session.flush()

        acc3 = PFAccount(id=uuid.uuid4(), citizen_id=c2.id, employment_id=emp3.id, member_id="KRN/BNG/0043210/000/0000555", status="ACTIVE")
        session.add(acc3)
        await session.flush()

        session.add(PFBalanceSnapshot(id=uuid.uuid4(), pf_account_id=acc3.id, snapshot_date=date(2024, 7, 31), employee_share=520000, employer_share=165000, interest_accrued=45000, total_balance=730000))

        # ----------------------------------------------------------------------
        # 3. Active-Correction Citizen: Vikram Patel
        # ----------------------------------------------------------------------
        c3 = Citizen(
            id=uuid.uuid4(),
            display_name="Vikram Patel",
            email="correction@pfcompass.demo",
            is_demo=True,
            date_of_birth=date(1988, 7, 5)
        )
        session.add(c3)
        await session.flush()

        session.add(AuthCredential(citizen_id=c3.id, password_hash=pwd_hash))

        uan4 = UANRecord(id=uuid.uuid4(), citizen_id=c3.id, uan="100333444555", is_primary=True, kyc_status="VERIFIED")
        session.add(uan4)
        await session.flush()

        emp4 = EmploymentHistory(
            id=uuid.uuid4(),
            citizen_id=c3.id,
            uan_id=uan4.id,
            employer_name="Zenith Logistics & Infra",
            date_of_joining=date(2016, 1, 10),
            date_of_exit=date(2022, 12, 31),
            exit_reason="RESIGNATION",
            is_data_verified=True
        )
        session.add(emp4)
        await session.flush()

        acc4 = PFAccount(id=uuid.uuid4(), citizen_id=c3.id, employment_id=emp4.id, member_id="GJ/AHM/0077889/000/0000333", status="ACTIVE")
        session.add(acc4)
        await session.flush()

        f3 = HealthFinding(
            id=uuid.uuid4(),
            citizen_id=c3.id,
            pf_account_id=acc4.id,
            employment_id=emp4.id,
            rule_version_id=rule_v2.id,
            rule_id="PFH-002",
            severity="HIGH",
            status="IN_CORRECTION",
            what_is_wrong="Date of exit missing from employer record despite resignation.",
            why_it_happened="Employer did not update date of exit on ECR portal upon resignation.",
            potential_impact="Full PF withdrawal claim Form 19 cannot be processed until exit date is marked.",
            correction_path={"summary": "Submit online Non-Employer Date of Exit update or Joint Declaration.", "form_numbers": ["JOINT-DECL"], "estimated_days": 10},
            evidence=[{"field": "date_of_exit", "expected": "2022-12-31", "actual": "NULL"}]
        )
        session.add(f3)
        await session.flush()

        # Active Case for Vikram
        case1 = Case(
            id=uuid.uuid4(),
            citizen_id=c3.id,
            case_type="CORRECTION",
            case_subtype="EXIT_DATE_CORRECTION",
            status="DOCUMENT_PENDING",
            finding_id=f3.id,
            opened_at=datetime.now(timezone.utc)
        )
        session.add(case1)
        await session.flush()

        # Events for CaseWise timeline
        session.add_all([
            CaseEvent(
                id=uuid.uuid4(),
                case_id=case1.id,
                event_type="CASE_OPENED",
                actor="CITIZEN",
                what_happened="Correction case initiated for missing Date of Exit.",
                why_it_happened="Citizen selected official correction path from PF Health report.",
                previous_status="OPEN",
                new_status="IN_CORRECTION"
            ),
            CaseEvent(
                id=uuid.uuid4(),
                case_id=case1.id,
                event_type="DOCUMENT_REQUESTED",
                actor="EPFO",
                what_happened="EPFO Field Office requested copy of Relieving Letter or Form 11.",
                why_it_happened="Verification required since exit date was not marked by employer within 60 days.",
                previous_status="IN_CORRECTION",
                new_status="DOCUMENT_PENDING"
            )
        ])

        # ----------------------------------------------------------------------
        # Demo Cases — synthetic, clearly seeded for demonstration purposes
        # All cases marked via citizen.is_demo=True and event actor provenance
        # ----------------------------------------------------------------------

        # CASE A: Rajesh Kumar — PF Withdrawal Claim, REJECTED
        # Official reason: intentionally null (not available from EPFO source)
        # PF Health connection: linked to f1 (Inoperative PF Account finding)
        # This demonstrates the trust model: known status, unknown official reason,
        # "Possible contributing factor" from PF Health
        case_rajesh = Case(
            id=uuid.uuid4(),
            citizen_id=c1.id,
            case_type="CLAIM",
            case_subtype="PF Withdrawal Claim",
            status="REJECTED",
            finding_id=f1.id,  # Links to Inoperative Account / KYC finding
            resolution_note=None,  # Official reason: NOT AVAILABLE. Do not invent one.
            opened_at=datetime(2026, 8, 10, 10, 30, 0, tzinfo=timezone.utc),
            resolved_at=datetime(2026, 8, 24, 14, 0, 0, tzinfo=timezone.utc),
        )
        session.add(case_rajesh)
        await session.flush()

        session.add_all([
            CaseEvent(
                id=uuid.uuid4(),
                case_id=case_rajesh.id,
                event_type="CLAIM_SUBMITTED",
                actor="CITIZEN",
                what_happened="PF full withdrawal claim submitted via EPFO Unified Member Portal.",
                why_it_happened="Citizen completed pre-submit readiness audit and submitted Form 19.",
                previous_status=None,
                new_status="SUBMITTED",
                occurred_at=datetime(2026, 8, 10, 10, 30, 0, tzinfo=timezone.utc),
            ),
            CaseEvent(
                id=uuid.uuid4(),
                case_id=case_rajesh.id,
                event_type="STATUS_UPDATED",
                actor="CITIZEN",
                what_happened="Claim status checked: Under Review — EPFO processing in progress.",
                why_it_happened="Citizen verified status on EPFO Member Portal and updated case record.",
                previous_status="SUBMITTED",
                new_status="UNDER_REVIEW",
                occurred_at=datetime(2026, 8, 14, 9, 0, 0, tzinfo=timezone.utc),
            ),
            CaseEvent(
                id=uuid.uuid4(),
                case_id=case_rajesh.id,
                event_type="STATUS_UPDATED",
                actor="CITIZEN",
                what_happened="Claim status changed to Rejected on EPFO Portal. No specific reason displayed.",
                why_it_happened="Citizen checked official EPFO Member Portal status and updated this record.",
                previous_status="UNDER_REVIEW",
                new_status="REJECTED",
                occurred_at=datetime(2026, 8, 24, 14, 0, 0, tzinfo=timezone.utc),
            ),
            CaseEvent(
                id=uuid.uuid4(),
                case_id=case_rajesh.id,
                event_type="PF_COMPASS_ANALYSIS",
                actor="SYSTEM",
                what_happened="PF Compass identified a possible contributing factor: your PF account with Acme Tech Solutions is marked INOPERATIVE and has an unresolved KYC mismatch.",
                why_it_happened="PF Health rule PFH-001 flagged this account. This may be relevant to the claim outcome, but EPFO has not confirmed it as the official rejection reason.",
                previous_status="REJECTED",
                new_status="REJECTED",
                occurred_at=datetime(2026, 8, 25, 8, 0, 0, tzinfo=timezone.utc),
            ),
        ])

        # CASE B: Vikram Patel — EXIT_DATE_CORRECTION (already seeded above as case1) ✓

        # CASE C: Ananya Sharma — PF Withdrawal Claim, SUBMITTED / UNDER PROCESS
        # No related PF Health finding — demonstrates normal tracking without issues
        case_ananya = Case(
            id=uuid.uuid4(),
            citizen_id=c2.id,
            case_type="CLAIM",
            case_subtype="PF Withdrawal Claim",
            status="UNDER_REVIEW",
            finding_id=None,  # No related PF Health issue
            resolution_note=None,
            opened_at=datetime(2026, 8, 20, 11, 15, 0, tzinfo=timezone.utc),
        )
        session.add(case_ananya)
        await session.flush()

        session.add_all([
            CaseEvent(
                id=uuid.uuid4(),
                case_id=case_ananya.id,
                event_type="CLAIM_SUBMITTED",
                actor="CITIZEN",
                what_happened="Full PF withdrawal claim submitted via EPFO Unified Member Portal (Form 19).",
                why_it_happened="All pre-submit checks passed. KYC verified. Bank account linked.",
                previous_status=None,
                new_status="SUBMITTED",
                occurred_at=datetime(2026, 8, 20, 11, 15, 0, tzinfo=timezone.utc),
            ),
            CaseEvent(
                id=uuid.uuid4(),
                case_id=case_ananya.id,
                event_type="STATUS_UPDATED",
                actor="CITIZEN",
                what_happened="Claim status updated to Under Review on EPFO Portal.",
                why_it_happened="Citizen verified current status on EPFO Member Portal.",
                previous_status="SUBMITTED",
                new_status="UNDER_REVIEW",
                occurred_at=datetime(2026, 8, 23, 9, 30, 0, tzinfo=timezone.utc),
            ),
        ])

        await session.commit()
        print("Demo data successfully seeded!")


if __name__ == "__main__":
    asyncio.run(seed_demo_citizens())
