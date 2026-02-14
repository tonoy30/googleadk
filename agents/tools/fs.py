from __future__ import annotations

import asyncio
import csv
import difflib
import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

# ---------------------------
# Helpers
# ---------------------------


def _resolve(path: str) -> Path:
    # Keep it simple: resolve relative to current working dir.
    return Path(path).expanduser().resolve()


def _sanitize_slug(s: str, max_len: int = 80) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:max_len] if len(s) > max_len else s


# ---------------------------
# Tools (plain functions)
# ADK wraps these with FunctionTool.
# ---------------------------


def fs_read_text(path: str, max_bytes: int = 2_000_000) -> Dict[str, Any]:
    """
    Read a UTF-8 text file from disk.

    Args:
        path: Absolute or relative file path.
        max_bytes: Safety limit for file size.
    Returns:
        {'status': 'success', 'path': '<resolved>', 'content': '<text>'}
        or {'status': 'error', 'error_message': '...'}
    """
    try:
        p = _resolve(path)
        if not p.exists() or not p.is_file():
            return {"status": "error", "error_message": f"File not found: {p}"}
        data = p.read_bytes()
        if len(data) > max_bytes:
            return {
                "status": "error",
                "error_message": f"File too large: {len(data)} > {max_bytes}",
            }
        return {"status": "success", "path": str(p), "content": data.decode("utf-8")}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def fs_write_text(path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Write a UTF-8 text file to disk.

    Args:
        path: Output file path.
        content: Text to write.
        overwrite: If False and file exists, return error.
    Returns:
        {'status': 'success', 'path': '<resolved>', 'bytes': N}
        or {'status': 'error', 'error_message': '...'}
    """
    try:
        p = _resolve(path)
        if p.exists() and not overwrite:
            return {
                "status": "error",
                "error_message": f"File exists and overwrite=false: {p}",
            }
        p.parent.mkdir(parents=True, exist_ok=True)
        b = content.encode("utf-8")
        p.write_bytes(b)
        return {"status": "success", "path": str(p), "bytes": len(b)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def fs_mkdir(path: str) -> Dict[str, Any]:
    """
    Create a directory (mkdir -p).

    Args:
        path: Directory path.
    Returns:
        {'status': 'success', 'path': '<resolved>', 'created': bool}
        or {'status': 'error', 'error_message': '...'}
    """
    try:
        p = _resolve(path)
        existed = p.exists()
        p.mkdir(parents=True, exist_ok=True)
        return {"status": "success", "path": str(p), "created": (not existed)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def fs_sha256(path: str) -> Dict[str, Any]:
    """
    Compute SHA-256 of a file.

    Args:
        path: File path.
    Returns:
        {'status': 'success', 'path': '<resolved>', 'sha256': '<hex>'}
        or {'status': 'error', 'error_message': '...'}
    """
    try:
        p = _resolve(path)
        if not p.exists() or not p.is_file():
            return {"status": "error", "error_message": f"File not found: {p}"}
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return {"status": "success", "path": str(p), "sha256": h.hexdigest()}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def text_unified_diff(
    from_text: str,
    to_text: str,
    from_name: str = "base",
    to_name: str = "tailored",
    context_lines: int = 3,
) -> Dict[str, Any]:
    """
    Create a unified diff between two strings.

    Returns:
        {'status': 'success', 'diff': '...', 'approx_changed_lines': N}
        or {'status': 'error', 'error_message': '...'}
    """
    try:
        a = from_text.splitlines(keepends=True)
        b = to_text.splitlines(keepends=True)
        diff_lines = list(
            difflib.unified_diff(
                a, b, fromfile=from_name, tofile=to_name, n=context_lines
            )
        )
        diff = "".join(diff_lines)
        changed = sum(
            1
            for line in diff_lines
            if (line.startswith("+") or line.startswith("-"))
            and not line.startswith(("+++", "---"))
        )
        return {"status": "success", "diff": diff, "approx_changed_lines": changed}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def csv_append_row(
    csv_path: str, header: List[str], row: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Append a row to a CSV file; create the file with header if it doesn't exist.

    Args:
        csv_path: Path to CSV.
        header: Ordered list of column names.
        row: Dict of values; missing keys become empty string.
    Returns:
        {'status': 'success', 'csv_path': '<resolved>', 'created': bool, 'appended': True}
        or {'status': 'error', 'error_message': '...'}
    """
    try:
        p = _resolve(csv_path)
        created = not p.exists()
        p.parent.mkdir(parents=True, exist_ok=True)

        out_row = {k: row.get(k, "") for k in header}

        mode = "a" if p.exists() else "w"
        with p.open(mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
            if created:
                writer.writeheader()
            writer.writerow(out_row)

        return {
            "status": "success",
            "csv_path": str(p),
            "created": created,
            "appended": True,
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def util_make_job_folder_name(
    job_id: str, job_title: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Create a deterministic folder name '<job_id>_<sanitized_job_title>' and store it in tool_context.state.

    Args:
        job_id: Deterministic job id.
        job_title: Role title.
        tool_context: ADK tool context (stateful).
    Returns:
        {'status': 'success', 'folder_name': '...'}
    """
    folder = f"{job_id}_{_sanitize_slug(job_title)}"
    tool_context.state["job_folder_name"] = folder
    return {"status": "success", "folder_name": folder}


# ---------------------------
# Toolset (BaseToolset)
# ---------------------------


class JobHuntToolset(BaseToolset):
    """
    Groups file IO + diff + CSV tools for the job hunt agents.
    """

    def __init__(self):
        super().__init__(tool_name_prefix="jobhubt")
        self._tools: List[BaseTool] = [
            FunctionTool(func=fs_read_text),
            FunctionTool(func=fs_write_text),
            FunctionTool(func=fs_mkdir),
            FunctionTool(func=fs_sha256),
            FunctionTool(func=text_unified_diff),
            FunctionTool(func=csv_append_row),
            FunctionTool(func=util_make_job_folder_name),
        ]

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        # You can add dynamic provisioning here based on readonly_context.state if needed.  [oai_citation:5‡Google GitHub](https://google.github.io/adk-docs/tools-custom/)
        return self._tools

    async def close(self) -> None:
        await asyncio.sleep(0)
