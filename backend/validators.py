from backend.models import ExtractedInformation, RiskFlag, ExtractedField, StatusEnum
import copy
from backend.logger import get_logger

logger = get_logger(__name__)

def validate_evidence(extracted: ExtractedInformation, raw_conversation: str) -> ExtractedInformation:
    """
    Validates that every field with status != missing has evidence,
    and that the evidence actually exists in the raw conversation.
    """
    validated = copy.deepcopy(extracted)
    conv_lower = raw_conversation.lower()
    
    def validate_field(field: ExtractedField, name: str):
        if field.status != StatusEnum.MISSING:
            if not field.evidence:
                logger.warning(f"Field {name} rejected: Missing evidence but status is {field.status.value}.")
                field.status = StatusEnum.MISSING
                field.value = None
                field.confidence = 0.0
                field.evidence = []
                return
            
            # Check if evidence is a substring of the conversation
            valid_evidence = []
            for ev in field.evidence:
                if ev.strip() and ev.lower() in conv_lower:
                    valid_evidence.append(ev)
                else:
                    logger.warning(f"Field {name} rejected evidence '{ev}': Not found in conversation.")
            
            if not valid_evidence:
                logger.warning(f"Field {name} rejected: No valid evidence found in text.")
                field.status = StatusEnum.MISSING
                field.value = None
                field.confidence = 0.0
                field.evidence = []
            else:
                field.evidence = valid_evidence

    # Validate individual fields
    validate_field(validated.weekly_summary, "weekly_summary")
    validate_field(validated.nutrition, "nutrition")
    validate_field(validated.exercise, "exercise")
    validate_field(validated.steps, "steps")
    validate_field(validated.sleep, "sleep")
    validate_field(validated.water_intake, "water_intake")
    validate_field(validated.symptoms, "symptoms")
    validate_field(validated.stress, "stress")
    validate_field(validated.energy, "energy")
    validate_field(validated.weight, "weight")
    validate_field(validated.engagement_level, "engagement_level")
    validate_field(validated.key_barriers, "key_barriers")
    validate_field(validated.pending_actions, "pending_actions")

    # Validate risk flags
    valid_risks = []
    for risk in validated.risk_flags:
        valid_evidence = [ev for ev in risk.evidence if ev.strip() and ev.lower() in conv_lower]
        if valid_evidence:
            risk.evidence = valid_evidence
            valid_risks.append(risk)
        else:
            logger.warning(f"Risk '{risk.title}' rejected: Evidence not found in conversation.")
    validated.risk_flags = valid_risks

    return validated
