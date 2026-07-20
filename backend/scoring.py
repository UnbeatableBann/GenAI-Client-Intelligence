from backend.models import ExtractedInformation
from typing import Dict, Any

def calculate_health_score(extracted: ExtractedInformation) -> Dict[str, Any]:
    """
    Rule-based deterministic health score calculation.
    Score is out of 100.
    """
    score = 0
    max_score = 0
    breakdown = {}
    reasons = []

    def evaluate_metric(metric_name: str, value_str: str, good_keywords: list, bad_keywords: list, weight: int = 10):
        nonlocal score, max_score
        max_score += weight
        if not value_str:
            breakdown[metric_name] = 0
            reasons.append(f"{metric_name.title()} data is missing (0/{weight}).")
            return
            
        val_lower = value_str.lower()
        if any(kw in val_lower for kw in good_keywords):
            score += weight
            breakdown[metric_name] = weight
            reasons.append(f"Good {metric_name} reported (+{weight}).")
        elif any(kw in val_lower for kw in bad_keywords):
            score += 0
            breakdown[metric_name] = 0
            reasons.append(f"Poor {metric_name} reported (+0).")
        else:
            # Partial score if ambiguous
            score += weight // 2
            breakdown[metric_name] = weight // 2
            reasons.append(f"{metric_name.title()} is adequate (+{weight//2}).")

    # Evaluate Sleep
    sleep_val = str(extracted.sleep.value) if extracted.sleep.value else ""
    evaluate_metric("sleep", sleep_val, ["7", "8", "9", "good", "rested"], ["low", "poor", "3", "4", "5", "bad"], weight=20)
    
    # Evaluate Water
    water_val = str(extracted.water_intake.value) if extracted.water_intake.value else ""
    evaluate_metric("water", water_val, ["adequate", "good", "2 liters", "3 liters", "gallons", "enough"], ["low", "poor", "little"], weight=15)

    # Evaluate Stress
    stress_val = str(extracted.stress.value) if extracted.stress.value else ""
    evaluate_metric("stress", stress_val, ["low", "none", "managed", "good"], ["high", "overwhelmed", "anxious", "bad", "pressure"], weight=20)

    # Evaluate Exercise
    exercise_val = str(extracted.exercise.value) if extracted.exercise.value else ""
    evaluate_metric("exercise", exercise_val, ["worked out", "gym", "ran", "walked", "active", "yes"], ["none", "missed", "no", "sedentary"], weight=20)
    
    # Evaluate Symptoms
    symptoms_val = str(extracted.symptoms.value) if extracted.symptoms.value else ""
    evaluate_metric("symptoms", symptoms_val, ["none", "feeling good", "better", "improved"], ["pain", "bloating", "fatigue", "acidity", "headache", "sick"], weight=25)

    final_score = int((score / max_score) * 100) if max_score > 0 else 0

    return {
        "overall_score": final_score,
        "breakdown": breakdown,
        "reasons": reasons
    }
