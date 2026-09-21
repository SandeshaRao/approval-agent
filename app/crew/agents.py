from __future__ import annotations

from typing import Any, Dict

from app.agents.aks_agent import AKSInfrastructureAnalyst
from app.agents.approval_agent import ApprovalDecisionAgent
from app.agents.capacity_agent import CapacityPlanningAgent
from app.agents.policy_agent import PolicyAgent


class CrewAgents:
    @staticmethod
    def run(request: Any, cluster_state: Dict[str, Any]) -> Dict[str, Any]:
        aks_analysis = AKSInfrastructureAnalyst.analyze()
        capacity = CapacityPlanningAgent.analyze(request, cluster_state)
        policy = PolicyAgent.validate(request, cluster_state)
        approval = ApprovalDecisionAgent.decide({"capacity": capacity, "policy": policy})
        return {
            "aks_analysis": aks_analysis,
            "capacity": capacity,
            "policy": policy,
            "approval": approval,
        }
