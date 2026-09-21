from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class DecisionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str
    reason: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None
    status: Optional[str] = None


class QuotaDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    status: str
    decision: str
    reason: str
    requested_cpu: str
    requested_memory: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
