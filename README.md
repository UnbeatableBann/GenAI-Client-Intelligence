# GenAI Client Intelligence Prototype

A production-inspired, LLM-powered application that analyzes client-coach conversations and generates a structured, evidence-grounded Client Intelligence Report.

## 🌟 Features

* **Conversation Ingestion:** Drag-and-drop file upload (`.txt`, `.csv`, `.md`) or raw text pasting.
* **Structured Data Extraction:** Utilizes Google Gemini to extract specific health metrics (Sleep, Water, Stress, Nutrition, etc.) into strict Pydantic schemas.
* **Hallucination Control:** Every extracted insight is programmatically verified against the raw conversation. Unsupported claims are automatically stripped out.
* **Health Score:** Deterministic, rule-based health scoring with explainable breakdowns.
* **Chronological Timeline:** Automatically reconstructs client events day-by-day.
* **Interactive Human Review:** Coaches can manually edit values, statuses, and confidence scores before saving the final report.

## 📋 Prerequisites

* **Python 3.12+**
* **[uv](https://github.com/astral-sh/uv)** (Python package and project manager)
* A valid **Google Gemini API Key**

## 🚀 Installation & Setup

1. **Navigate to the project directory**:
   ```bash
   cd "GenAI Client Intelligence"
   ```

2. **Set up the environment and install dependencies** using `uv`:
   ```bash
   uv sync
   ```

3. **Configure the environment variables**:
   * Copy the example environment file (if you haven't already):
     ```bash
     cp .env.example .env
     ```
   * Open `.env` and add your Gemini API key:
     ```env
     GEMINI_API_KEY=your_api_key_here
     ```

## 💻 Running the Application

Start the Streamlit dashboard using `uv`:

```bash
uv run streamlit run app.py
```

The application will launch in your default web browser at `http://localhost:8501`.

## 🧪 Testing with Sample Data

We have included a sample conversation to help you test the pipeline immediately!

1. Open the running Streamlit dashboard.
2. Look at the sidebar on the left side under **"Or Upload File"**.
3. Drag and drop the `sample_conversation.txt` file (located in the root of this project) into the upload box.
4. Click **Process Conversation**.

You will see the pipeline extract metrics, calculate the health score, detect risk flags, and generate a chronological timeline based on the sample data.

## 🏗️ Architecture

* **`app.py`**: Streamlit frontend, interactive UI, and rendering logic.
* **`backend/models.py`**: Strict Pydantic v2 schemas defining the required data structures.
* **`backend/prompts.py`**: Prompt engineering with isolation tags (`<conversation>`) to prevent prompt injection.
* **`backend/validators.py`**: Logic to verify LLM evidence against the raw input to prevent hallucinations.
* **`backend/llm_service.py`**: Gemini API integration with `tenacity`-powered exponential backoff retries.
* **`backend/scoring.py`**: Rule-based logic for health score generation.
* **`tests/`**: Unit tests for validation and scoring logic using `pytest`.
