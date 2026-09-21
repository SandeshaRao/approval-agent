from __future__ import annotations

from typing import Any, Dict, List, Optional


class AKSUsageTool:
    """Deterministic AKS monitoring helper for quota evaluation."""

    @staticmethod
    def get_aks_cluster_usage() -> Dict[str, Any]:
        return {
            "cluster": "production-aks",
            "node_pool": "system",
            "node_count": 8,
            "cpu": {
                "capacity": "64 cores",
                "allocatable": 56,
                "requested": 32,
                "utilization_percent": 57,
            },
            "memory": {
                "capacity": "256Gi",
                "allocatable": 224,
                "requested": 120,
                "utilization_percent": 54,
            },
            "pending_pods": 2,
            "unschedulable_pods": 0,
            "namespace_usage": {"payments": {"cpu": 7, "memory": 30}},
        }

    @staticmethod
    def get_node_pool_details() -> Dict[str, Any]:
        return {
            "name": "system",
            "current_nodes": 8,
            "min_nodes": 2,
            "max_nodes": 20,
            "vm_sku": "Standard_D8s_v5",
            "autoscale_enabled": True,
        }

    @staticmethod
    def get_kubernetes_nodes() -> List[Dict[str, Any]]:
        return [
            {"name": "aks-node-1", "ready": True, "cpu_allocatable": 7, "memory_allocatable": 28},
            {"name": "aks-node-2", "ready": True, "cpu_allocatable": 7, "memory_allocatable": 28},
        ]

    @staticmethod
    def get_pending_pods() -> List[Dict[str, Any]]:
        return [{"namespace": "payments", "name": "pending-job", "cpu_request": "2", "memory_request": "8Gi"}]

    @staticmethod
    def get_namespace_usage() -> Dict[str, Any]:
        return {"payments": {"cpu_requests": 12, "memory_requests": 48, "quota": {"cpu": "20", "memory": "100Gi"}}}


def get_aks_cluster_usage() -> Dict[str, Any]:
    return AKSUsageTool.get_aks_cluster_usage()


def get_node_pool_details() -> Dict[str, Any]:
    return AKSUsageTool.get_node_pool_details()


def get_kubernetes_nodes() -> List[Dict[str, Any]]:
    return AKSUsageTool.get_kubernetes_nodes()


def get_pending_pods() -> List[Dict[str, Any]]:
    return AKSUsageTool.get_pending_pods()


def get_namespace_usage() -> Dict[str, Any]:
    return AKSUsageTool.get_namespace_usage()
