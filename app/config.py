from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "quota-approval"
    api_prefix: str = "/quota"
    azure_subscription_id: str = ""
    azure_resource_group: str = ""
    aks_cluster_name: str = ""
    aks_node_pool_name: str = ""
    azure_use_managed_identity: bool = False
    azure_client_id: str = ""
    azure_tenant_id: str = ""
    azure_auth_mode: str = "default"
    azure_use_live_data: bool = False
    teams_webhook_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    cpu_utilization_threshold: float = 70.0
    memory_utilization_threshold: float = 70.0
    max_auto_scale_nodes: int = 5
    request_timeout_seconds: int = 30
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
