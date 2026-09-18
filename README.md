# Resume Analyzer

A working full-stack prototype that parses resumes, extracts skills/experience, computes a match score against a job description, and provides actionable feedback.

## Features
- **File Parsing**: Supports PDF, DOCX, and TXT via `PyPDF2` and `python-docx`.
- **Skill Extraction**: Uses a combination of regex and exact string matching against a built-in taxonomy of ~100 common tech skills.
- **Scoring Engine**: Weighted score based on Skills Match (65%), Experience (20%), and Education (15%).
- **LLM Summary (Optional)**: Automatically generates a qualitative fit summary if an `OPENAI_API_KEY` is provided.
- **Authentication**: JWT based user login and registration with beautiful UI.
- **Frontend UI**: Built-in test UI served directly via FastAPI and Jinja2 templates.
- **Recruiter Dashboard**: A dedicated UI panel for users to view and compare all their previously analyzed candidates.

## How to run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) Set your OpenAI API key for LLM summaries:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key"
   ```

3. Start the server on a different port (e.g., 8080):
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

4. Open [http://localhost:8080](http://localhost:8080) in your browser.

## API Documentation
Once the server is running, you can access the automatic interactive API documentation at:
- Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)

## Future Extensions
- **OCR for scanned PDFs**: Integrate `pytesseract` for image-based PDFs.
- **Semantic Embeddings**: Replace exact matching with sentence transformers to catch synonyms (e.g., "K8s" vs "Kubernetes").
