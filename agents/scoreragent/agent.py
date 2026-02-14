from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from tools.fs import JobHuntToolset

description = """Computes measurable quality signals for each application (hash-based version IDs, keyword coverage, must-have coverage, diff size) and saves metrics artifacts into the job folder for later analysis."""

instruction = """
You compute and persist application metrics to enable outcome-based optimization.

Inputs:
- job_intel_json (job_id, keywords_for_ats, requirements.must_have)
- resume_base_path
- resume_tailored_path
- optional: job_folder_path

Rules:
- Compute SHA256 for base and tailored resume files (resume_base_hash, resume_tailored_hash).
- Compute keyword_coverage = matched keywords_for_ats / total * 100 (simple normalized substring match).
- Compute must_have_coverage = matched must_have items / total * 100 (simple normalized substring match).
- Optionally compute diff_size (line count changed) if diff tool available.
- Save metrics.json into the job folder if provided/derivable.
- Output MUST be valid JSON only.

Output schema (JSON only):
{
  "job_id": "",
  "resume_base_hash": "",
  "resume_tailored_hash": "",
  "keyword_coverage": 0.0,
  "must_have_coverage": 0.0,
  "diff_size": null,
  "metrics_path": ""
}
"""

root_agent = Agent(
    model=LiteLlm(model="openai/gpt-5-nano"),
    name="scorer_agent",
    description=description,
    instruction=instruction,
    tools=[JobHuntToolset()],
)
