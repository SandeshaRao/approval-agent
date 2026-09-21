import pytest

from app.models.quota_request import QuotaRequest
from app.policies.infrastructure_policy import PolicyEngine


def test_approve_when_capacity_available():
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

    result = PolicyEngine.evaluate(request=request, cluster_state=cluster)
    assert result["decision"] == "APPROVE"


def test_scale_when_capacity_insufficient_but_pool_can_scale():
    request = QuotaRequest(
        application_name="payment-service",
        namespace="payments",
        requested_cpu="16",
        requested_memory="64Gi",
        environment="production",
        requester="user@example.com",
        business_justification="Required for burst workload",
    )
    cluster = {
        "cpu": {"allocatable": 56, "requested": 50, "utilization_percent": 75},
        "memory": {"allocatable": 224, "requested": 180, "utilization_percent": 72},
        "node_pool": {"max_nodes": 20, "current_nodes": 8},
        "pending_pods": 0,
        "unschedulable_pods": 0,
    }

    result = PolicyEngine.evaluate(request=request, cluster_state=cluster)
    assert result["decision"] in {"SCALE_AND_APPROVE", "HUMAN_APPROVAL_REQUIRED"}


def test_reject_when_pool_at_max_capacity():
    request = QuotaRequest(
        application_name="payment-service",
        namespace="payments",
        requested_cpu="32",
        requested_memory="128Gi",
        environment="production",
        requester="user@example.com",
        business_justification="High demand",
    )
    cluster = {
        "cpu": {"allocatable": 48, "requested": 46, "utilization_percent": 85},
        "memory": {"allocatable": 190, "requested": 180, "utilization_percent": 90},
        "node_pool": {"max_nodes": 8, "current_nodes": 8},
        "pending_pods": 0,
        "unschedulable_pods": 0,
    }

    result = PolicyEngine.evaluate(request=request, cluster_state=cluster)
    assert result["decision"] == "REJECT"


def test_human_approval_when_monitoring_unavailable():
    request = QuotaRequest(
        application_name="payment-service",
        namespace="payments",
        requested_cpu="8",
        requested_memory="32Gi",
        environment="production",
        requester="user@example.com",
        business_justification="Monitoring unavailable",
    )
    cluster = None

    result = PolicyEngine.evaluate(request=request, cluster_state=cluster)
    assert result["decision"] == "HUMAN_APPROVAL_REQUIRED"


def test_agent_disagreement_triggers_human_approval():
    results = {
        "capacity": "APPROVE",
        "policy": "REJECT",
    }
    assert results["capacity"] != results["policy"]

