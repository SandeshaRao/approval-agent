from __future__ import annotations

from typing import Any, Dict

from app.tools.aks_tools import get_aks_cluster_usage, get_kubernetes_nodes, get_namespace_usage, get_node_pool_details, get_pending_pods


class AKSInfrastructureAnalyst:
    @staticmethod
    def analyze() -> Dict[str, Any]:
        return {
            "cluster_usage": get_aks_cluster_usage(),
            "node_pool": get_node_pool_details(),
            "nodes": get_kubernetes_nodes(),
            "pending_pods": get_pending_pods(),
            "namespace_usage": get_namespace_usage(),
        }
