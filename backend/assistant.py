import json
import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.models import FinalReport, AssistantResponse, AssistantSource, StatusEnum
from backend.llm_service import extract_structured_data
from backend.prompts import ASSISTANT_PROMPT
from backend.logger import get_logger

logger = get_logger(__name__)

def process_assistant_query(question: str, report: FinalReport, conversation: str) -> AssistantResponse:
    logger.info("Using LLM for query.")
    report_json = report.model_dump_json()
    
    relevant_evidence = ""
    for k, v in report.extracted_info.model_dump().items():
        if isinstance(v, dict) and 'evidence' in v and len(v['evidence']) > 0:
            relevant_evidence += f"{k.capitalize()} Evidence: {v['evidence']}\n"
    
    prompt = ASSISTANT_PROMPT.format(
        question=question,
        conversation=conversation,
        structured_data=report_json,
        relevant_evidence=relevant_evidence
    )
    
    result = extract_structured_data("", prompt, AssistantResponse)
    
    # Evidence Validation
    valid_sources = []
    conv_lower = conversation.lower()
    for s in result.sources:
        if s.quote.lower() in conv_lower:
            valid_sources.append(s)
        else:
            logger.warning(f"Assistant evidence rejected '{s.quote}': Not found in conversation.")
    
    if len(valid_sources) == 0 and len(result.sources) > 0:
        result.status = "error"
        result.answer = "I could not find supporting evidence to safely answer this question."
        result.sources = []
    else:
        result.sources = valid_sources
        
    return result

def generate_suggested_questions(report: FinalReport) -> List[str]:
    questions = []
    info = report.extracted_info
    
    if info.risk_flags:
        questions.append(f"Why is the risk '{info.risk_flags[0].title}' generated?")
        
    if info.stress.status != StatusEnum.MISSING and info.stress.value:
        questions.append(f"Why is stress marked as {info.stress.value}?")
        
    if info.symptoms.status != StatusEnum.MISSING and info.symptoms.value:
        symptoms = info.symptoms.value.split(",")
        if symptoms:
            first_symptom = symptoms[0].strip()
            questions.append(f"Show all mentions of {first_symptom.lower()}.")
            
    if info.sleep.status != StatusEnum.MISSING:
        questions.append("How did sleep change during the week?")
        
    if info.nutrition.status != StatusEnum.MISSING:
        questions.append("Summarize nutrition only.")
        
    if info.key_barriers.status != StatusEnum.MISSING and info.key_barriers.value:
        questions.append("What barriers prevented adherence?")
        
    questions.append("Compare Day 1 and Day 8.")
    questions.append("Generate follow-up questions for tomorrow.")
    
    defaults = [
        "What changed this week?",
        "Did the client improve overall?",
        "Show evidence for coach recommendation."
    ]
    for d in defaults:
        if len(questions) < 8 and d not in questions:
            questions.append(d)
            
    return questions[:8]
