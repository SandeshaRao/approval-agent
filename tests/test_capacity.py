from app.models.quota_request import QuotaRequest
from app.services.capacity_service import CapacityService


def test_capacity_analyzes_fit():
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
    }
    result = CapacityService.analyze(request, cluster)
    assert result["request_can_fit"] is True
