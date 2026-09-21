from __future__ import annotations

from typing import Any, Dict

from app.models.quota_request import QuotaRequest
from app.services.capacity_service import CapacityService


class CapacityPlanningAgent:
    @staticmethod
    def analyze(request: QuotaRequest, cluster_state: Dict[str, Any]) -> Dict[str, Any]:
        return CapacityService.analyze(request, cluster_state)
