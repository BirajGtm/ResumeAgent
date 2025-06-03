**Readme created using GitHub Copilot - might have inconsistancies**
# Resume Agentic Pipeline

A modular pipeline for parsing, analyzing, and tailoring resumes using LLMs (Large Language Models) to match job descriptions. This project is designed for developers and job seekers who want to automate the process of customizing resumes for specific job postings. This also creates a cover letter if you select the option in the UI.

## Preview
![Preview](https://i.imgur.com/8I97MC7.png)

## Demo Video

[![Watch the demo](https://img.youtube.com/vi/H5wdAmH2okM/0.jpg)](https://www.youtube.com/watch?v=H5wdAmH2okM&ab_channel=BirajGautam)


## Features

- **Resume Parsing:** Converts plain text resumes into structured data.
- **Job Description Analysis:** Extracts key requirements and skills from job descriptions.
- **LLM-Powered Tailoring:** Uses models like GPT-4o to rewrite and structure resume sections for optimal alignment with job postings.
- **Section-Based Processing:** Supports tailoring the entire resume or specific sections.
- **Output as PDF:** Can edit and download pdf files. 

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

- (Recommended) Create a conda environment:

```bash
conda create -n resume_agentic python=3.10
conda activate resume_agentic
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Usage

- Run the main pipeline script (example):

```bash
python app.py
```
### 4. Workflow
- You need to provide a master resume - with all your experience and background in .docx file.
- Tailored resume output will be available in the UI. You can edit and download a pdf.
- If you are using one resume, upload it only first time, it will then use cached data to create tailored resumes and you dont need to select resume file over and over again.
- If you wanna change and work with new resume just select a new resume from Choose file option.
- Select LLM you wanna use for tailoring resume or evaluating it.
- Try exploring other features on your own as I have not mentioned everything here.
- Custom file name does not work at the moment.

## Configuration

- **Model Selection:** Set your preferred LLM model from the list in the web UI, before that make your you have your API keys in the `.env` file (e.g., `gpt-4o`).
- Note: Can use Gemini upto 2.0 flash.

## Development

- All core logic is in the `modules/` and `routes/`  directory.
- See `modules/tailor_agent.py` for the main tailoring logic and prompt engineering.

## Ignore Rules

- Sensitive files and directories (`input/`, `.env`, `output/`, `cache/`, etc.) are excluded via `.gitignore`.

## License

MIT License

---

**Note:** This project is for educational and personal use. Always review AI-generated content before submitting to employers.