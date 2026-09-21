from __future__ import annotations

from typing import Any, Dict


class ApprovalDecisionAgent:
    @staticmethod
    def decide(results: Dict[str, Any]) -> Dict[str, Any]:
        decisions = [results.get("capacity", {}).get("decision", "HUMAN_APPROVAL_REQUIRED"), results.get("policy", {}).get("decision", "HUMAN_APPROVAL_REQUIRED")]
        if any(item == "REJECT" for item in decisions):
            return {"decision": "HUMAN_APPROVAL_REQUIRED", "reason": "Agent disagreement detected; policy and capacity results conflict"}
        if all(item == "APPROVE" for item in decisions):
            return {"decision": "APPROVE", "reason": "All agents agree the request can be approved safely"}
        return {"decision": "HUMAN_APPROVAL_REQUIRED", "reason": "Unable to confidently determine a safe decision"}
