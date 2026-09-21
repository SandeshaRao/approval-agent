from __future__ import annotations

from typing import Any, Dict

from app.models.quota_request import QuotaRequest
from app.policies.infrastructure_policy import PolicyEngine


class PolicyAgent:
    @staticmethod
    def validate(request: QuotaRequest, cluster_state: Dict[str, Any]) -> Dict[str, Any]:
        return PolicyEngine.evaluate(request, cluster_state)
