from google import genai
from google.genai import types
from google.genai.errors import APIError
import os
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from backend.logger import get_logger

logger = get_logger(__name__)

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)

# Retry only on API errors (like 503, 429), not ValidationErrors which mean the model output structure was bad 
# or 400 which means bad request. Actually APIError covers 400 as well, but tenacity retries on APIError.
# For a production app, we would inspect the status code, but for now we'll retry APIError.
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(APIError),
    reraise=True
)
def _call_gemini_with_retry(client, prompt: str, text: str, schema_class: type[BaseModel]) -> str:
    logger.info(f"Calling Gemini API for schema {schema_class.__name__}")
    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=[prompt, text],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema_class,
            temperature=0.1,
        )
    )
    return response.text

def extract_structured_data(text: str, prompt: str, schema_class: type[BaseModel]) -> BaseModel:
    client = get_client()
    try:
        response_text = _call_gemini_with_retry(client, prompt, text, schema_class)
        return schema_class.model_validate_json(response_text)
    except ValidationError as ve:
        logger.error(f"Schema validation failed: {ve}")
        raise ValueError(f"LLM returned invalid schema: {ve}")
    except APIError as api_err:
        logger.error(f"API Error after retries: {api_err}")
        raise RuntimeError(f"LLM API failure: {api_err}")
    except Exception as e:
        logger.error(f"Unexpected error in LLM extraction: {e}")
        raise RuntimeError(f"LLM extraction failed: {e}")
