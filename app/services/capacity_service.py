from __future__ import annotations

from typing import Any, Dict

from app.models.quota_request import QuotaRequest


class CapacityService:
    @staticmethod
    def analyze(request: QuotaRequest, cluster_state: Dict[str, Any]) -> Dict[str, Any]:
        cpu_allocatable = float(cluster_state.get("cpu", {}).get("allocatable", 0))
        memory_allocatable = float(cluster_state.get("memory", {}).get("allocatable", 0))
        requested_cpu = float(request.cpu_cores())
        requested_memory = float(request.memory_gib())

        available_cpu = cpu_allocatable - requested_cpu
        available_memory = memory_allocatable - requested_memory
        can_fit = available_cpu > 0 and available_memory > 0

        return {
            "request_can_fit": can_fit,
            "additional_nodes_required": 0 if can_fit else 1,
            "reason": "Insufficient allocatable memory" if available_memory <= 0 else "Insufficient allocatable CPU" if available_cpu <= 0 else "Request fits within allocatable capacity",
            "confidence": 0.95,
            "available_cpu": available_cpu,
            "available_memory": available_memory,
        }
