from backend.models import ExtractedInformation, ReasoningResult, FinalReport
from backend.prompts import EXTRACTION_PROMPT, REASONING_PROMPT
from backend.llm_service import extract_structured_data
from backend.validators import validate_evidence
from backend.logger import get_logger

logger = get_logger(__name__)

def preprocess_conversation(raw_text: str) -> str:
    # Normalize formatting and remove unnecessary whitespace
    lines = raw_text.split('\n')
    cleaned = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned)

def process_pipeline(raw_conversation: str) -> FinalReport:
    if not raw_conversation.strip():
        logger.error("Empty conversation provided.")
        raise ValueError("Empty conversation provided.")

    logger.info("Starting pipeline processing.")
    # Step 2: Preprocessing
    cleaned_conv = preprocess_conversation(raw_conversation)

    # Format prompts with the conversation data
    extraction_prompt_formatted = EXTRACTION_PROMPT.format(conversation=cleaned_conv)

    # Step 3 & 4: LLM Extraction and Schema Validation
    logger.info("Extracting structured information...")
    extracted = extract_structured_data(
        text="Extract the information based on the instructions.", 
        prompt=extraction_prompt_formatted, 
        schema_class=ExtractedInformation
    )

    # Step 5: Evidence Validation
    logger.info("Validating evidence...")
    validated = validate_evidence(extracted, cleaned_conv)

    # Step 6: Reasoning
    logger.info("Generating reasoning...")
    reasoning_prompt_formatted = REASONING_PROMPT.format(structured_data=validated.model_dump_json())
    reasoning = extract_structured_data(
        text="Generate reasoning based on the provided structured JSON data.", 
        prompt=reasoning_prompt_formatted, 
        schema_class=ReasoningResult
    )

    logger.info("Pipeline processing completed successfully.")
    # Step 7: Final Report for Dashboard
    return FinalReport(extracted_info=validated, reasoning=reasoning)
