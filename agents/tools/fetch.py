import asyncio
from typing import Any, Dict, List, Optional

import requests
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool


def web_fetch_html(url: str) -> Dict[str, Any]:
    """
    Fetch raw HTML content of a webpage.
    """
    try:
        response = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()

        return {
            "status": "success",
            "url": url,
            "html": response.text,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }


class WebToolset(BaseToolset):
    def __init__(self, tool_name_prefix: str = "web_"):
        super().__init__(tool_name_prefix=tool_name_prefix)

        self._tools: List[BaseTool] = [
            FunctionTool(func=web_fetch_html),
        ]

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        return self._tools

    async def close(self) -> None:
        await asyncio.sleep(0)
