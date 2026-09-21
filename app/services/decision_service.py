from __future__ import annotations

from typing import Any, Dict, Optional

from app.models.quota_request import QuotaRequest
from app.policies.infrastructure_policy import PolicyEngine


class DecisionService:
    @staticmethod
    def decide(request: QuotaRequest, cluster_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        policy_result = PolicyEngine.evaluate(request=request, cluster_state=cluster_state)
        return policy_result
