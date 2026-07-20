# GenAI Client Intelligence Prototype

This is a functional prototype that analyzes a client-coach conversation and generates a structured, evidence-grounded Client Intelligence Report.

The primary goal of this system is **accuracy, explainability, and hallucination control**. Every insight produced by the AI is traceable back to the original conversation.

## Features
- **Multi-Stage Pipeline**: Conversation -> Preprocessing -> LLM Extraction -> Schema Validation -> Reasoning -> Dashboard -> Human Review
- **Hallucination Prevention**: The system strictly extracts verified facts. If evidence is not present, information is marked as missing.
- **Evidence Validation**: Validates that extracted values have corresponding quotes from the text.
- **Structured Output**: Uses `google-genai` and `Pydantic` for reliable, type-safe data schemas.
- **Interactive Dashboard**: A minimalist, professional UI built with Streamlit.

## Setup Instructions

1. **Prerequisites**: Python 3.12+ and `uv` are recommended.
2. **Install Dependencies**:
   ```bash
   uv sync
   ```
3. **Configure Environment**:
   - Rename `.env.example` to `.env`.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Architecture
- `app.py`: Streamlit frontend application.
- `backend/models.py`: Pydantic data models for structured LLM extraction.
- `backend/prompts.py`: Carefully designed prompts with strict hallucination control rules.
- `backend/validators.py`: Evidence validation logic to reject unsupported facts.
- `backend/llm_service.py`: Service layer integrating the Google GenAI SDK.
- `backend/pipeline.py`: Orchestrates the step-by-step processing pipeline.
