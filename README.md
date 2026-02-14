# 🎯 JobHunt AI — Multi-Agent Job Application Pipeline

An autonomous multi-agent system built with **Google ADK (Agent Development Kit)** that orchestrates the entire job application workflow: job parsing, resume tailoring, cover letter generation, and application tracking—all with anti-hallucination safeguards.

---

## ✨ Features

- **🤖 Multi-Agent Architecture** — Specialized agents coordinate through a central controller
- **📄 LaTeX Resume Tailoring** — Automatically customizes your resume for each job posting
- **📝 Cover Letter Generation** — Creates factual, evidence-based cover letters
- **🔍 ATS Optimization** — Extracts and matches keywords for applicant tracking systems
- **🛡️ Anti-Hallucination Guards** — Strict validation prevents fabricated claims
- **📊 Application Tracking** — Generates CSV entries for systematic tracking
- **🌍 Multi-Language Support** — German and English job postings supported

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       CONTROLLER AGENT                              │
│            (Orchestrates pipeline, validates outputs)               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Job Intel    │     │ Resume Analyser │     │  Cover Letter   │
│    Agent      │     │     Agent       │     │     Agent       │
│               │     │                 │     │                 │
│ Parses JDs,   │     │ Tailors LaTeX   │     │ Generates fact- │
│ extracts      │     │ resumes, tracks │     │ based letters   │
│ requirements  │     │ ATS keywords    │     │                 │
└───────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Scorer     │     │  Application    │     │   JobHunt &     │
│    Agent      │     │    Tracker      │     │   Web Toolsets  │
│               │     │                 │     │                 │
│ Computes hash │     │ CSV generation  │     │ File I/O, HTTP  │
│ & coverage %  │     │ & tracking      │     │ fetch, SHA256   │
└───────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 📦 Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd googleadk

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

### Environment Variables

Set your LLM API key:

```bash
export OPENAI_API_KEY="your-api-key"
```

---

## 🚀 Usage

### Running the Agent Pipeline

```bash
# Using Google ADK CLI
adk run agents/jobhunt

# Or start the ADK web interface
adk web agents/jobhunt
```

### Pipeline Inputs

The controller agent requires:

| Input | Required | Description |
|-------|----------|-------------|
| `job_url` | Yes* | URL to the job posting |
| `raw_jd_text` | Yes* | Raw job description text (alternative to URL) |
| `base_resume_path` | Yes | Path to your base LaTeX resume (e.g., `./data/resume.tex`) |

*Either `job_url` or `raw_jd_text` must be provided.

### Example Interaction

```
User: Apply to this job: https://example.com/jobs/senior-engineer

Agent: {
  "status": "waiting_for_input",
  "missing_fields": ["base_resume_path"],
  "message": "Please provide the file path to your base LaTeX resume."
}

User: ./data/resume.tex

Agent: [Executes full pipeline...]
{
  "job_intel_json": { ... },
  "updated_resume_latex": "...",
  "cover_letter": "...",
  "application_tracker_csv": "..."
}
```

---

## 🤖 Agent Details

### Controller Agent (`jobhunt`)
The orchestrator that manages the entire pipeline. It:
- Validates inputs before starting
- Calls sub-agents in the correct sequence
- Enforces anti-hallucination rules
- Returns consolidated output bundle

### Job Intel Agent (`jobintel`)
Parses job postings (URL or raw text) and extracts:
- Must-have vs. nice-to-have requirements
- ATS-relevant keywords
- Tailoring guidance for resume and cover letter
- Red flags (visa issues, vague scope, etc.)

### Resume Analyser Agent (`resumeanalyser`)
Tailors your LaTeX resume:
- Creates job-specific folder: `<job_id>_<sanitized_title>/`
- Saves tailored resume without overwriting the base
- Tracks keyword coverage and flags missing unverifiable skills
- Ensures LaTeX remains compilable

### Cover Letter Agent (`coverletter`)
Generates professional cover letters:
- Uses only verified facts from your resume
- Maps experience to job requirements
- Supports German and English
- Includes requirement-to-evidence mapping

### Scorer Agent (`scoreragent`)
Computes quality metrics:
- SHA-256 hashes for version control
- Keyword coverage percentage
- Must-have requirements coverage
- Diff size between base and tailored resume

### Application Tracker Agent (`applicationtracker`)
Generates CSV tracking entries with:
- Job ID, company, role, location
- Links to tailored resume and cover letter
- Application status and notes

---

## 🛠️ Tools

### JobHunt Toolset
| Tool | Description |
|------|-------------|
| `fs_read_text` | Read UTF-8 text files |
| `fs_write_text` | Write UTF-8 text files |
| `fs_mkdir` | Create directories |
| `fs_sha256` | Compute file checksums |
| `text_unified_diff` | Generate unified diffs |
| `csv_append_row` | Append rows to CSV files |
| `util_make_job_folder_name` | Generate sanitized folder names |

### Web Toolset
| Tool | Description |
|------|-------------|
| `web_fetch_html` | Fetch HTML from job posting URLs |

---

## 📁 Project Structure

```
googleadk/
├── agents/
│   ├── jobhunt/          # Controller agent (orchestrator)
│   ├── jobintel/         # Job posting parser
│   ├── resumeanalyser/   # Resume tailoring agent
│   ├── coverletter/      # Cover letter generator
│   ├── scoreragent/      # Quality metrics calculator
│   ├── applicationtracker/  # CSV tracking generator
│   └── tools/
│       ├── fs.py         # File system toolset
│       └── fetch.py      # Web fetch toolset
├── data/
│   └── resume.tex        # Your base LaTeX resume
├── main.py
├── pyproject.toml
└── README.md
```

---

## 🔒 Anti-Hallucination Design

The system enforces strict anti-hallucination rules:

1. **No Fabrication** — Agents cannot invent roles, metrics, skills, or certifications
2. **Verified Facts Only** — Cover letters use only facts extracted from your resume
3. **Transparent Gaps** — Missing information is flagged in `missing_unverifiable` fields
4. **Validation Checkpoints** — Controller validates each agent's output before proceeding
5. **JSON-Only Communication** — All inter-agent data is machine-parseable

---

## 📋 Output Schema

The final output bundle:

```json
{
  "job_intel_json": {
    "source": { "job_url": "", "language": "en" },
    "role": { "title": "", "level": "", "employment_type": "" },
    "requirements": {
      "must_have": [...],
      "nice_to_have": [...]
    },
    "keywords_for_ats": [...],
    "tailoring_guidance": { ... }
  },
  "updated_resume_latex": "\\documentclass{...}",
  "cover_letter": "Dear Hiring Manager...",
  "application_tracker_csv": "job_id,company,role_title,..."
}
```

---

## 🧪 Development

```bash
# Run linting
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy agents/
```

---

## 🙏 Acknowledgments

Built with [Google ADK](https://google.github.io/adk-docs/) and [LiteLLM](https://github.com/BerriAI/litellm).
