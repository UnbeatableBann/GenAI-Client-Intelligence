from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional
from enum import Enum

class StatusEnum(str, Enum):
    CONFIRMED_FACT = "confirmed_fact"
    CLIENT_REPORTED = "client_reported"
    AI_INFERENCE = "ai_inference"
    MISSING = "missing"

class ExtractedField(BaseModel):
    value: Optional[str] = Field(default=None, description="The extracted value as a string, or null if missing.")
    status: StatusEnum = Field(description="The status of the extracted information.")
    evidence: List[str] = Field(default_factory=list, description="Direct quotes from the conversation supporting the value. Must not be empty strings if status is not missing.")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0.")

class RiskFlag(BaseModel):
    title: str = Field(description="Title of the risk flag.")
    severity: str = Field(description="Severity of the risk (e.g., High, Medium, Low).")
    reason: str = Field(description="Reason for the risk flag.")
    evidence: List[str] = Field(default_factory=list, description="Direct quotes supporting this risk.")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0.")

class ExtractedInformation(BaseModel):
    weekly_summary: ExtractedField
    nutrition: ExtractedField
    exercise: ExtractedField
    steps: ExtractedField
    sleep: ExtractedField
    water_intake: ExtractedField
    symptoms: ExtractedField
    stress: ExtractedField
    energy: ExtractedField
    weight: ExtractedField
    engagement_level: ExtractedField
    key_barriers: ExtractedField
    pending_actions: ExtractedField
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)

class TimelineEntry(BaseModel):
    day: str = Field(description="The day or timeframe (e.g., 'Day 1', 'Monday').")
    events: List[str] = Field(description="List of key events or symptoms for this day.")

class TrendEntry(BaseModel):
    metric: str = Field(description="The metric being tracked (e.g., Sleep, Stress).")
    trend: str = Field(description="The trend value (e.g., Improving, Declining, Stable).")

class ReasoningResult(BaseModel):
    trends: List[TrendEntry] = Field(default_factory=list, description="Trends for metrics like sleep, stress, energy.")
    timeline: List[TimelineEntry] = Field(default_factory=list, description="Chronological timeline of events extracted from the conversation.")
    coach_recommendation: str = Field(description="Recommendation for the coach based on the extracted data.")
    suggested_follow_up_questions: List[str] = Field(default_factory=list, description="Follow-up questions based on missing information or repeated symptoms/barriers.")

class FinalReport(BaseModel):
    extracted_info: ExtractedInformation
    reasoning: ReasoningResult

class AssistantSource(BaseModel):
    day: Optional[str] = Field(default=None)
    speaker: Optional[str] = Field(default=None)
    quote: str

class AssistantResponse(BaseModel):
    answer: str
    confidence: float
    status: str
    reasoning: str
    sources: List[AssistantSource] = Field(default_factory=list)
