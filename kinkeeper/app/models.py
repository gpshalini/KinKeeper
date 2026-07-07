from typing import List, Literal
from pydantic import BaseModel, Field

class Event(BaseModel):
    person: str = Field(..., description="Name of the person or 'Unknown person'")
    event_type: Literal["birthday", "anniversary", "remembrance day", "death anniversary"] = Field(
        ..., description="Type of family event"
    )
    inferred_date: str = Field(..., description="Inferred date in YYYY-MM-DD format")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence level of the extraction")
    source_snippet: str = Field(..., description="Redacted chat snippet context for the event")
    reminder_timing: List[str] = Field(
        default_factory=lambda: ["7 days before", "1 day before", "day of event"],
        description="List of reminder timings"
    )
    suggested_action: Literal["Draft message", "Send e-card", "Find flowers", "Reminder to call"] = Field(
        ..., description="Suggested next action"
    )
    status: Literal["captured", "needs_review", "edited", "deleted"] = Field(
        "captured", description="Status of the captured event"
    )

class ExtractedEvent(BaseModel):
    person: str = Field(..., description="Name of the person being wished, or 'Unknown person' if not clear")
    event_type: Literal["birthday", "anniversary", "remembrance day", "death anniversary"] = Field(
        ..., description="Type of event detected"
    )
    inferred_date: str = Field(..., description="The date of the event in YYYY-MM-DD format (use the message date if not explicitly specified)")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence level of the extraction")
    source_snippet: str = Field(..., description="The exact chat message text associated with the event")

class ExtractionResult(BaseModel):
    events: List[ExtractedEvent] = Field(default_factory=list)

class IdentityResolvedEvent(BaseModel):
    person: str = Field(..., description="Standardized name of the person or 'Unknown person'")
    event_type: Literal["birthday", "anniversary", "remembrance day", "death anniversary"] = Field(
        ..., description="Type of event detected"
    )
    inferred_date: str = Field(..., description="The date of the event in YYYY-MM-DD format (after merging/deduplication)")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence level of the extraction")
    source_snippet: str = Field(..., description="The exact chat message text associated with the event (can be multiple merged)")

class IdentityResult(BaseModel):
    events: List[IdentityResolvedEvent] = Field(default_factory=list)

class ConciergeEvent(BaseModel):
    person: str = Field(..., description="Standardized name of the person or 'Unknown person'")
    event_type: Literal["birthday", "anniversary", "remembrance day", "death anniversary"] = Field(
        ..., description="Type of event detected"
    )
    inferred_date: str = Field(..., description="The date of the event in YYYY-MM-DD format")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence level of the extraction")
    source_snippet: str = Field(..., description="The exact chat message text associated with the event")
    suggested_action: Literal["Draft message", "Send e-card", "Find flowers", "Reminder to call"] = Field(
        ..., description="Suggested next action"
    )
    suggested_message: str = Field(..., description="Warm, context-aware greeting draft")

class ConciergeResult(BaseModel):
    events: List[ConciergeEvent] = Field(default_factory=list)

class ChatInput(BaseModel):
    chat_text: str = Field(..., description="The raw WhatsApp chat text to process")

class EventResponseSchema(BaseModel):
    person: str
    event_type: str
    inferred_date: str
    confidence: str
    source_snippet: str
    reminder_timing: List[str]
    suggested_action: str
    status: str
    suggested_message: str = ""

class WorkflowOutput(BaseModel):
    captured_events: List[EventResponseSchema]
    needs_review: List[EventResponseSchema]
    skipped_summary: dict
    privacy_summary: dict
    audit_summary: dict
    suggested_actions: List[dict]


