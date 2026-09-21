from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuotaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(..., min_length=1)
    namespace: str = Field(..., min_length=1)
    requested_cpu: str = Field(..., min_length=1)
    requested_memory: str = Field(..., min_length=1)
    environment: str = Field(..., min_length=1)
    requester: str = Field(..., min_length=1)
    business_justification: str = Field(..., min_length=1)

    @field_validator("requested_cpu")
    @classmethod
    def validate_cpu(cls, value: str) -> str:
        try:
            parsed = float(value)
        except ValueError as exc:
            raise ValueError("requested_cpu must be numeric") from exc
        if parsed <= 0:
            raise ValueError("requested_cpu must be greater than zero")
        return value

    @field_validator("requested_memory")
    @classmethod
    def validate_memory(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized.endswith("gi") or normalized.endswith("g") or normalized.endswith("mi") or normalized.endswith("m"):
            return value
        raise ValueError("requested_memory must be a valid Kubernetes memory quantity like 32Gi or 512Mi")

    def cpu_cores(self) -> float:
        return float(self.requested_cpu)

    def memory_gib(self) -> float:
        value = self.requested_memory.strip().lower()
        if value.endswith("gi"):
            return float(value[:-2])
        if value.endswith("mi"):
            return float(value[:-2]) / 1024
        if value.endswith("g"):
            return float(value[:-1])
        if value.endswith("m"):
            return float(value[:-1]) / 1024
        raise ValueError(f"Unsupported memory quantity: {self.requested_memory}")
