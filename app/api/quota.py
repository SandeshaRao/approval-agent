from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.crew.orchestrator import AKSLiveCrew
from app.models.quota_request import QuotaRequest
from app.services.decision_service import DecisionService
from app.services.notification_service import NotificationService

router = APIRouter(tags=["quota"])
_REQUEST_STORE: Dict[str, Dict[str, Any]] = {}


@router.post("/quota/request")
def submit_quota_request(request: QuotaRequest) -> Dict[str, Any]:
    request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"

    cluster_state = {
        "cpu": {"allocatable": 48, "requested": 20, "utilization_percent": 50},
        "memory": {"allocatable": 200, "requested": 90, "utilization_percent": 55},
        "node_pool": {"max_nodes": 20, "current_nodes": 8},
        "pending_pods": 0,
        "unschedulable_pods": 0,
    }

    try:
        crew_result = AKSLiveCrew.run(request)
        cluster_state = crew_result.get("cluster_state", cluster_state)
        decision = DecisionService.decide(request, cluster_state)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail="Decision processing failed") from exc

    decision_name = decision["decision"]
    status_map = {
        "APPROVE": "APPROVED",
        "SCALE_AND_APPROVE": "SCALED_AND_APPROVED",
        "REJECT": "REJECTED",
        "HUMAN_APPROVAL_REQUIRED": "PENDING_HUMAN_APPROVAL",
    }
    status_value = status_map.get(decision_name, "FAILED")

    response = {
        "request_id": request_id,
        "status": status_value,
        "decision": decision_name,
        "reason": decision["reason"],
        "requested_cpu": request.requested_cpu,
        "requested_memory": request.requested_memory,
        "evidence": decision.get("evidence", {}),
        "crew_analysis": crew_result,
    }
    _REQUEST_STORE[request_id] = response
    NotificationService.send_decision_notification(request_id, request, response)
    return response


@router.get("/quota/request/{request_id}")
def get_request_status(request_id: str) -> Dict[str, Any]:
    record = _REQUEST_STORE.get(request_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return record
