from __future__ import annotations

from typing import Any, Dict

from app.models.quota_request import QuotaRequest
from app.tools.teams_tools import build_teams_message_card, send_teams_notification


class NotificationService:
    @staticmethod
    def send_decision_notification(request_id: str, request: QuotaRequest, response: Dict[str, Any]) -> Dict[str, Any]:
        title = "Infrastructure Quota Decision"
        summary = f"Quota request {request_id} for {request.application_name}"
        decision = response.get("decision", "UNKNOWN")
        status = response.get("status", "UNKNOWN")
        theme_color = "0076D7"
        if status == "APPROVED":
            theme_color = "2EB886"
        elif status == "REJECTED":
            theme_color = "D13438"
        elif status == "PENDING_HUMAN_APPROVAL":
            theme_color = "FF8C00"

        facts = [
            {"name": "Request ID", "value": request_id},
            {"name": "Application", "value": request.application_name},
            {"name": "Environment", "value": request.environment},
            {"name": "Requested CPU", "value": request.requested_cpu},
            {"name": "Requested Memory", "value": request.requested_memory},
            {"name": "Decision", "value": decision},
            {"name": "Status", "value": status},
        ]
        payload = build_teams_message_card(
            title=title,
            summary=summary,
            facts=facts,
            text=f"Decision: {decision}\nStatus: {status}\nReason: {response.get('reason', 'No reason provided')}",
            theme_color=theme_color,
        )
        return send_teams_notification(payload)
