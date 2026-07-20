import pytest
from backend.models import ExtractedInformation, ExtractedField, StatusEnum, RiskFlag
from backend.validators import validate_evidence

def create_mock_report():
    field = ExtractedField(value="Good", status=StatusEnum.CLIENT_REPORTED, evidence=["feeling well"], confidence=1.0)
    return ExtractedInformation(
        weekly_summary=field, nutrition=field, exercise=field, steps=field, sleep=field,
        water_intake=field, symptoms=field, stress=field, energy=field, weight=field,
        engagement_level=field, key_barriers=field, pending_actions=field,
        risk_flags=[RiskFlag(title="test", severity="Low", reason="test", evidence=["feeling well"], confidence=1.0)]
    )

def test_validate_evidence_success():
    report = create_mock_report()
    raw_text = "Client said they are feeling well today."
    validated = validate_evidence(report, raw_text)
    
    assert validated.symptoms.status == StatusEnum.CLIENT_REPORTED
    assert "feeling well" in validated.symptoms.evidence

def test_validate_evidence_missing_in_text():
    report = create_mock_report()
    # Evidence "feeling well" is hallucinated, not in raw_text
    raw_text = "Client said they are feeling sick today."
    validated = validate_evidence(report, raw_text)
    
    # Validation should reject the field
    assert validated.symptoms.status == StatusEnum.MISSING
    assert validated.symptoms.value is None
    assert len(validated.symptoms.evidence) == 0

def test_validate_evidence_empty_evidence():
    report = create_mock_report()
    report.symptoms.evidence = [""]
    raw_text = "Client said they are feeling well today."
    validated = validate_evidence(report, raw_text)
    
    # Validation should reject because evidence is empty string
    assert validated.symptoms.status == StatusEnum.MISSING
