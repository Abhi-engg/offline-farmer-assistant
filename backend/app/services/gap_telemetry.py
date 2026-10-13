"""
Offline Gap Telemetry & Unhandled Query Collection Service.
Captures:
1. Missing Knowledge: Farmer asked about a crop/pest not in local ICAR database.
2. Unhandled / Ambiguous Intent: Queries where intent engine scored low confidence.
3. Missing Slots: Query lacked crop or specific symptoms.
4. Farmer Feedback: Thumbs down or explicit negative ratings.

Stores events locally in an append-only JSONL file and provides clustering/export.
Zero cloud dependency; completely functional offline.
"""
import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
GAP_LOG_FILE = os.path.join(DATA_DIR, "unhandled_gaps.jsonl")

@dataclass
class GapEvent:
    timestamp: str
    query: str
    language: str
    gap_type: str  # MISSING_KNOWLEDGE, AMBIGUOUS_INTENT, MISSING_SLOTS, USER_FEEDBACK
    intent: str
    slots: Dict[str, Any]
    rag_matches_count: int
    top_rag_score: float
    answer_preview: str
    feedback: Optional[str] = None
    resolved: bool = False

class GapTelemetryService:
    def __init__(self, log_path: str = GAP_LOG_FILE):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                pass

    def evaluate_and_record(
        self,
        query: str,
        language: str,
        intent_res: Any,
        rag_docs: List[Dict[str, Any]],
        answer: str,
        is_handled: bool
    ) -> Optional[GapEvent]:
        """
        Automatically classifies if a turn represents an unhandled gap.
        If yes, appends it to the local gap ledger.
        """
        gap_type = None
        top_score = rag_docs[0].get("score", 0.0) if rag_docs else 0.0

        if not is_handled or intent_res.intent == "OUT_OF_SCOPE_OR_AMBIGUOUS":
            gap_type = "AMBIGUOUS_INTENT"
        elif len(rag_docs) == 0 or top_score < 2.0:
            # Recognized intent but missing authoritative ICAR guide
            gap_type = "MISSING_KNOWLEDGE"
        elif intent_res.intent in ["PEST_DISEASE_CONTROL", "FERTILIZER_SOIL_MANAGEMENT"] and "crop" not in intent_res.slots:
            gap_type = "MISSING_SLOTS"

        if gap_type:
            event = GapEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                query=query,
                language=language,
                gap_type=gap_type,
                intent=intent_res.intent,
                slots=intent_res.slots,
                rag_matches_count=len(rag_docs),
                top_rag_score=top_score,
                answer_preview=answer[:120] if answer else "",
                resolved=False
            )
            self._append_to_log(event)
            return event
        return None

    def record_user_feedback(
        self,
        query: str,
        language: str,
        rating: str,  # 'helpful' or 'unhelpful'
        comment: Optional[str] = None
    ):
        """Records explicit user/field-worker rating."""
        event = GapEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            query=query,
            language=language,
            gap_type="USER_FEEDBACK",
            intent="FEEDBACK_REPORT",
            slots={},
            rag_matches_count=0,
            top_rag_score=0.0,
            answer_preview="",
            feedback=f"{rating}: {comment or ''}".strip(),
            resolved=False
        )
        self._append_to_log(event)

    def _append_to_log(self, event: GapEvent):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def get_recent_gaps(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves most recent gap events."""
        events = []
        if os.path.exists(self.log_path):
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines):
                    if line.strip():
                        try:
                            events.append(json.loads(line))
                        except Exception:
                            continue
                    if len(events) >= limit:
                        break
        return events

    def get_summary(self) -> Dict[str, Any]:
        """Provides high-level gap clustering and analytics."""
        events = self.get_recent_gaps(limit=500)
        gap_types: Dict[str, int] = {}
        missing_crops: Dict[str, int] = {}
        languages: Dict[str, int] = {}

        for e in events:
            gt = e.get("gap_type", "UNKNOWN")
            gap_types[gt] = gap_types.get(gt, 0) + 1

            lang = e.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1

            crop = e.get("slots", {}).get("crop")
            if crop:
                missing_crops[crop] = missing_crops.get(crop, 0) + 1

        return {
            "total_gaps_recorded": len(events),
            "by_gap_type": gap_types,
            "by_language": languages,
            "frequently_asked_crops": missing_crops,
            "log_path": self.log_path
        }

# Global gap telemetry service singleton
gap_telemetry = GapTelemetryService()
