from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_invalid_request_returns_400():
    response = client.post(
        "/quota/request",
        json={
            "application_name": "bad-service",
            "namespace": "payments",
            "requested_cpu": "-4",
            "requested_memory": "invalid",
            "environment": "production",
            "requester": "user@example.com",
            "business_justification": "Broken request",
        },
    )
    assert response.status_code == 400


def test_valid_request_returns_successful_response():
    response = client.post(
        "/quota/request",
        json={
            "application_name": "payment-service",
            "namespace": "payments",
            "requested_cpu": "4",
            "requested_memory": "16Gi",
            "environment": "production",
            "requester": "user@example.com",
            "business_justification": "Required for production workload",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"APPROVED", "SCALED_AND_APPROVED", "PENDING_HUMAN_APPROVAL", "REJECTED"}
    assert "request_id" in payload
