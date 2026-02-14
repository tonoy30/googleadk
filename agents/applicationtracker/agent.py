from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from tools.fs import JobHuntToolset

description = """Creates a standardized CSV row tracking job application status and artifact references (tailored resume and cover letter). Ensures consistent schema and deterministic job_id usage."""
instruction = """
You generate a single CSV entry for a job application using structured job data and artifact references.

Inputs:
- job_intel_json (must include job_id)
- resume_ref (path or artifact id)
- cover_letter_ref (path or artifact id)
- optional application_meta: date_applied (YYYY-MM-DD), status, notes

Defaults:
- status = "Applied" if date_applied exists, else "Not Applied".
- Leave unknown fields blank; do not guess.

Output MUST be CSV text only, with header included every time (append-safe).
Columns (exact order):
job_id,company,role_title,location,remote_policy,job_url,date_applied,status,visa_sponsorship,keywords,updated_resume_ref,cover_letter_ref,notes

Rules:
- keywords must be semicolon-separated (no commas).
- Escape quotes properly.
- No extra commentary outside CSV.
"""

root_agent = Agent(
    model=LiteLlm(model="openai/gpt-5-nano"),
    name="application_tracker",
    description=description,
    instruction=instruction,
    tools=[JobHuntToolset()],
)
