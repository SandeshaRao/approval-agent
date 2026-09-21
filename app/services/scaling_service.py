from __future__ import annotations

from typing import Any, Dict

from app.config import get_settings
from app.tools.azure_tools import calculate_required_nodes, check_nodes_ready, scale_node_pool, validate_azure_quota


class ScalingService:
    @staticmethod
    def evaluate_scale(request_cpu: float, request_memory: float, cluster_state: Dict[str, Any]) -> Dict[str, Any]:
        settings = get_settings()
        node_pool = cluster_state.get("node_pool", {})
        current_nodes = int(node_pool.get("current_nodes", 0))
        max_nodes = int(node_pool.get("max_nodes", 0))
        allocatable_cpu = float(cluster_state.get("cpu", {}).get("allocatable", 0))

        cap = validate_azure_quota(
            settings.azure_subscription_id,
            settings.azure_resource_group,
            settings.aks_cluster_name,
        )
        if not cap["valid"]:
            return {"can_scale": False, "reason": cap["reason"], "scaling": None}

        required = calculate_required_nodes(current_nodes, allocatable_cpu, request_cpu, max_nodes)
        if not required["can_scale"]:
            return {"can_scale": False, "reason": "Node pool reached its configured maximum capacity", "scaling": required}

        scaling = scale_node_pool(node_pool.get("name", settings.aks_node_pool_name), current_nodes, required["additional_nodes_required"], max_nodes)
        if not scaling["scaled"]:
            return {"can_scale": False, "reason": scaling["reason"], "scaling": required}

        ready = check_nodes_ready()
        if not ready:
            return {"can_scale": False, "reason": "Scale operation started but nodes have not become ready yet", "scaling": scaling}

        return {"can_scale": True, "reason": "Node pool scaling validated", "scaling": scaling}
