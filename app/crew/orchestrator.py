from __future__ import annotations

import os
from typing import Any, Dict

from crewai import Agent, Crew, Task
from crewai.tools import BaseTool

from app.config import get_settings
from app.tools.azure_tools import fetch_cluster_state, get_cluster_metrics, scale_node_pool


class AKSClusterUsageTool(BaseTool):
    name: str = "get_aks_cluster_usage"
    description: str = "Retrieve AKS cluster and node-pool state from Azure or deterministic local state."

    def _run(self, *args, **kwargs) -> Dict[str, Any]:
        return fetch_cluster_state()


class AKSMetricsTool(BaseTool):
    name: str = "get_azure_monitor_metrics"
    description: str = "Retrieve Azure Monitor metrics for AKS cluster CPU and memory utilization."

    def _run(self, *args, **kwargs) -> Dict[str, Any]:
        return get_cluster_metrics()


class AKSScaleTool(BaseTool):
    name: str = "scale_aks_node_pool"
    description: str = "Scale the configured AKS node pool by a given number of nodes using Azure SDK if enabled."

    def _run(self, node_pool_name: str, current_node_count: int, additional_nodes: int, max_nodes: int, resource_group: str | None = None, cluster_name: str | None = None) -> Dict[str, Any]:
        return scale_node_pool(node_pool_name, current_node_count, additional_nodes, max_nodes, resource_group, cluster_name)


class AKSLiveCrew:
    @staticmethod
    def run(request: Any) -> Dict[str, Any]:
        settings = get_settings()
        aks_usage_tool = AKSClusterUsageTool()
        monitor_tool = AKSMetricsTool()
        scale_tool = AKSScaleTool()

        cluster_state = aks_usage_tool._run()
        metrics = monitor_tool._run()

        llm_configured = bool(settings.llm_api_key or os.getenv("OPENAI_API_KEY"))
        if not llm_configured:
            node_pool_name = settings.aks_node_pool_name or (cluster_state or {}).get("node_pool") or "default"
            scale_action = {
                "scaled": False,
                "reason": "No AKS node pool configured; deterministic fallback skipped scaling",
                "previous_nodes": int((cluster_state or {}).get("node_pool_details", {}).get("current_nodes", 0) or 0),
                "additional_nodes": 0,
                "new_node_count": int((cluster_state or {}).get("node_pool_details", {}).get("current_nodes", 0) or 0),
            }
            if settings.aks_node_pool_name:
                try:
                    scale_action = scale_tool._run(
                        settings.aks_node_pool_name,
                        int((cluster_state or {}).get("node_pool_details", {}).get("current_nodes", 0) or 0),
                        0,
                        int((cluster_state or {}).get("node_pool_details", {}).get("max_nodes", 0) or 0),
                        settings.azure_resource_group,
                        settings.aks_cluster_name,
                    )
                except Exception:
                    scale_action = {
                        "scaled": False,
                        "reason": "Scaling was skipped because no live Azure scale was requested",
                        "previous_nodes": int((cluster_state or {}).get("node_pool_details", {}).get("current_nodes", 0) or 0),
                        "additional_nodes": 0,
                        "new_node_count": int((cluster_state or {}).get("node_pool_details", {}).get("current_nodes", 0) or 0),
                    }
            return {
                "crew_mode": "tool_direct_execution",
                "crew_output": "Deterministic Azure tool execution executed without LLM execution.",
                "cluster_state": cluster_state,
                "metrics": metrics,
                "scale_action": scale_action,
            }

        analyst = Agent(
            role="AKS Infrastructure Analyst",
            goal="Collect AKS and Azure Monitor evidence before approving quota requests.",
            backstory="You inspect real cluster state and monitor data to judge whether infrastructure can safely support a request.",
            tools=[aks_usage_tool, monitor_tool],
            verbose=False,
        )

        scale_agent = Agent(
            role="Scaling Decision Agent",
            goal="Determine whether AKS should scale to accommodate the quota request.",
            backstory="You check node pool limits and execute safe, validated scaling operations.",
            tools=[scale_tool],
            verbose=False,
        )

        analyst_task = Task(
            description=f"Analyze AKS cluster state for application {request.application_name} and request CPU {request.requested_cpu}, memory {request.requested_memory}.",
            agent=analyst,
            expected_output="Structured AKS cluster and Azure Monitor analysis.",
        )

        scale_task = Task(
            description="If the request cannot fit, calculate whether a node-pool scale is required and return the scale action details.",
            agent=scale_agent,
            expected_output="Structured scale recommendation with real Azure SDK details.",
        )

        crew = Crew(agents=[analyst, scale_agent], tasks=[analyst_task, scale_task], verbose=False)
        outcome = crew.kickoff()
        return {"crew_mode": "llm_execution", "crew_output": str(outcome), "cluster_state": cluster_state, "metrics": metrics}
