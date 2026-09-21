from __future__ import annotations

from typing import Any, Dict, Optional

from app.config import get_settings
from app.models.quota_request import QuotaRequest


class PolicyEngine:
    @staticmethod
    def evaluate(request: QuotaRequest, cluster_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        settings = get_settings()

        if cluster_state is None:
            return {
                "decision": "HUMAN_APPROVAL_REQUIRED",
                "reason": "AKS monitoring data unavailable",
                "evidence": {"monitoring_data": None},
            }

        cpu_utilization = float(cluster_state.get("cpu", {}).get("utilization_percent", 0))
        memory_utilization = float(cluster_state.get("memory", {}).get("utilization_percent", 0))
        allocatable_cpu = float(cluster_state.get("cpu", {}).get("allocatable", 0))
        allocatable_memory = float(cluster_state.get("memory", {}).get("allocatable", 0))
        requested_cpu = float(request.cpu_cores())
        requested_memory = float(request.memory_gib())

        if cpu_utilization >= settings.cpu_utilization_threshold or memory_utilization >= settings.memory_utilization_threshold:
            node_pool = cluster_state.get("node_pool", {})
            max_nodes = int(node_pool.get("max_nodes", 0))
            current_nodes = int(node_pool.get("current_nodes", 0))
            if current_nodes >= max_nodes:
                return {
                    "decision": "REJECT",
                    "reason": "Node pool has reached its configured maximum capacity",
                    "evidence": {
                        "cpu_utilization": cpu_utilization,
                        "memory_utilization": memory_utilization,
                        "requested_cpu": request.requested_cpu,
                        "requested_memory": request.requested_memory,
                    },
                }

            if allocatable_cpu - requested_cpu > 0 and allocatable_memory - requested_memory > 0:
                return {
                    "decision": "SCALE_AND_APPROVE",
                    "reason": "Cluster utilization is above threshold but scaling can safely accommodate the requested quota",
                    "evidence": {
                        "cpu_utilization": cpu_utilization,
                        "memory_utilization": memory_utilization,
                        "requested_cpu": request.requested_cpu,
                        "requested_memory": request.requested_memory,
                    },
                }

            return {
                "decision": "HUMAN_APPROVAL_REQUIRED",
                "reason": "Cluster is near capacity and Azure sizing cannot be validated safely",
                "evidence": {
                    "cpu_utilization": cpu_utilization,
                    "memory_utilization": memory_utilization,
                    "requested_cpu": request.requested_cpu,
                    "requested_memory": request.requested_memory,
                },
            }

        if allocatable_cpu >= requested_cpu and allocatable_memory >= requested_memory:
            return {
                "decision": "APPROVE",
                "reason": "AKS cluster has sufficient capacity below configured utilization threshold",
                "evidence": {
                    "cpu_utilization": cpu_utilization,
                    "memory_utilization": memory_utilization,
                    "requested_cpu": request.requested_cpu,
                    "requested_memory": request.requested_memory,
                },
            }

        return {
            "decision": "HUMAN_APPROVAL_REQUIRED",
            "reason": "Requested resources cannot be safely accommodated without additional validation",
            "evidence": {
                "cpu_utilization": cpu_utilization,
                "memory_utilization": memory_utilization,
                "requested_cpu": request.requested_cpu,
                "requested_memory": request.requested_memory,
            },
        }
