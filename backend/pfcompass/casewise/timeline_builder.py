from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from pfcompass.models import CaseEvent


@dataclass
class StatusChange:
    from_status: Optional[str]
    to_status: Optional[str]


@dataclass
class TimelineItem:
    id: str
    event_type: str
    occurred_at: datetime
    actor: str
    actor_label: str
    what_happened: str
    why_it_happened: Optional[str] = None
    status_change: Optional[StatusChange] = None
    evidence: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_action_required: bool = False


@dataclass
class CaseTimeline:
    case_id: str
    current_status: str
    items: List[TimelineItem] = field(default_factory=list)
    total_duration_days: float = 0.0


class TimelineBuilder:
    """Reconstructs the full case timeline from an ordered sequence of events."""

    @staticmethod
    def _humanize_actor(actor: str) -> str:
        mapping = {
            "CITIZEN": "Citizen",
            "EPFO": "EPFO Field Office",
            "EMPLOYER": "Employer",
            "SYSTEM": "PF Compass Engine",
        }
        return mapping.get(actor.upper(), actor)

    def build_timeline(self, case_id: str, events: List[CaseEvent]) -> CaseTimeline:
        if not events:
            return CaseTimeline(case_id=str(case_id), current_status="UNKNOWN", items=[])

        # Events are ordered by occurred_at ASC
        timeline_items: List[TimelineItem] = []

        for event in events:
            status_change = None
            if event.previous_status or event.new_status:
                status_change = StatusChange(
                    from_status=event.previous_status,
                    to_status=event.new_status,
                )

            is_action_req = event.event_type in (
                "DOCUMENT_REQUESTED",
                "ACTION_REQUIRED",
                "EMPLOYER_CLARIFICATION_NEEDED",
            )

            item = TimelineItem(
                id=str(event.id),
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                actor=event.actor,
                actor_label=self._humanize_actor(event.actor),
                what_happened=event.what_happened,
                why_it_happened=event.why_it_happened,
                status_change=status_change,
                evidence=event.evidence,
                metadata=event.metadata_payload,
                is_action_required=is_action_req,
            )
            timeline_items.append(item)

        first_time = events[0].occurred_at
        last_time = events[-1].occurred_at
        duration_days = round((last_time - first_time).total_seconds() / 86400.0, 1) if first_time and last_time else 0.0

        latest_status = events[-1].new_status or events[-1].previous_status or "OPEN"

        return CaseTimeline(
            case_id=str(case_id),
            current_status=latest_status,
            items=timeline_items,
            total_duration_days=max(0.0, duration_days),
        )
