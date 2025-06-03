 **Readme created using GitHub Copilot - might have inconsistancies**
# Resume Agentic Pipeline

A modular pipeline for parsing, analyzing, and tailoring resumes using LLMs (Large Language Models) to match job descriptions. This project is designed for developers and job seekers who want to automate the process of customizing resumes for specific job postings.

## Features

- **Resume Parsing:** Converts plain text resumes into structured data.
- **Job Description Analysis:** Extracts key requirements and skills from job descriptions.
- **LLM-Powered Tailoring:** Uses models like GPT-4o to rewrite and structure resume sections for optimal alignment with job postings.
- **Section-Based Processing:** Supports tailoring the entire resume or specific sections.
- **Output in JSON or Markdown:** Structured output for easy integration with other tools or direct use.

## Project Structure

```
resume_agentic_pipeline/
├── input/                # Raw resumes and job descriptions
├── output/               # Tailored resumes and logs
├── cache/                # Temporary or cached files
├── modules/              # Core Python modules (parsing, tailoring, etc.)
│   └── tailor_agent.py
├── .env.example          # Example environment variables
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/resume_agentic_pipeline.git
cd resume_agentic_pipeline
```

### 2. Set Up Environment

- Copy `.env.example` to `.env` and fill in your API keys and settings.

```bash
cp .env.example .env
```

- (Optional) Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Usage

- Place your resume in `input/uploaded_resume.txt`.
- Place your job description in `input/job_description.txt`.
- Run the main pipeline script (example):

```bash
python main.py
```

- Tailored resume output will be saved in the `output/` directory.

## Configuration

- **Model Selection:** Set your preferred LLM model in the `.env` file (e.g., `gpt-4o`).
- **API Keys:** Store your OpenAI or other LLM provider keys in `.env`.

## Development

- All core logic is in the `modules/` directory.
- See `modules/tailor_agent.py` for the main tailoring logic and prompt engineering.

## Ignore Rules

- Sensitive files and directories (`input/`, `.env`, `output/`, `cache/`, etc.) are excluded via `.gitignore`.

## License

MIT License

---

**Note:** This project is for educational and personal use. Always review AI-generated content before submitting to employers.