from app.models.quota_request import QuotaRequest
from app.services.decision_service import DecisionService


def test_decision_service_approve():
    request = QuotaRequest(
        application_name="payment-service",
        namespace="payments",
        requested_cpu="4",
        requested_memory="16Gi",
        environment="production",
        requester="user@example.com",
        business_justification="Required for production workload",
    )
    cluster = {
        "cpu": {"allocatable": 48, "requested": 20, "utilization_percent": 50},
        "memory": {"allocatable": 200, "requested": 90, "utilization_percent": 55},
        "node_pool": {"max_nodes": 20, "current_nodes": 8},
        "pending_pods": 0,
        "unschedulable_pods": 0,
    }
    result = DecisionService.decide(request, cluster)
    assert result["decision"] == "APPROVE"


def test_decision_service_human_approval():
    request = QuotaRequest(
        application_name="payment-service",
        namespace="payments",
        requested_cpu="8",
        requested_memory="32Gi",
        environment="production",
        requester="user@example.com",
        business_justification="Cannot determine safely",
    )
    result = DecisionService.decide(request, None)
    assert result["decision"] == "HUMAN_APPROVAL_REQUIRED"
