import pytest
from backend.models import ExtractedInformation, ExtractedField, StatusEnum
from backend.scoring import calculate_health_score

def test_calculate_health_score():
    field = ExtractedField(value="Good", status=StatusEnum.CLIENT_REPORTED, evidence=[""], confidence=1.0)
    
    report = ExtractedInformation(
        weekly_summary=field, nutrition=field,
        exercise=ExtractedField(value="ran 5k", status=StatusEnum.CLIENT_REPORTED, evidence=[""], confidence=1.0),
        steps=field,
        sleep=ExtractedField(value="8 hours", status=StatusEnum.CLIENT_REPORTED, evidence=[""], confidence=1.0),
        water_intake=ExtractedField(value="3 liters", status=StatusEnum.CLIENT_REPORTED, evidence=[""], confidence=1.0),
        symptoms=ExtractedField(value="none", status=StatusEnum.CLIENT_REPORTED, evidence=[""], confidence=1.0),
        stress=ExtractedField(value="low", status=StatusEnum.CLIENT_REPORTED, evidence=[""], confidence=1.0),
        energy=field, weight=field, engagement_level=field, key_barriers=field, pending_actions=field, risk_flags=[]
    )
    
    score_data = calculate_health_score(report)
    assert score_data["overall_score"] > 80
    assert "breakdown" in score_data
    assert score_data["breakdown"]["sleep"] == 20
