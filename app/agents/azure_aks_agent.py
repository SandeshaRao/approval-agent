from __future__ import annotations

from typing import Any, Dict

from app.tools.azure_tools import fetch_cluster_state


class AzureAKSAgent:
    @staticmethod
    def gather_cluster_state() -> Dict[str, Any]:
        return fetch_cluster_state()
