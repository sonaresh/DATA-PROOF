from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class Decision(str, Enum):
    ALLOW = "ALLOW"
    CONSTRAIN = "CONSTRAIN"
    REVIEW = "REVIEW"
    DENY = "DENY"

class GovernanceState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    classification: str = "internal"
    purpose: str
    lineage_complete: bool = True
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    age_hours: float = Field(default=0.0, ge=0.0)
    region: str = "us-east-1"
    disclosure_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    requested_fields: list[str] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    downstream: str = "internal"
    policy_version: str = "v1.0.0"

class GovernanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str
    actor: str
    role_authorized: bool = True
    operation: Literal["READ","JOIN","TRANSFORM","SHARE","EXPORT","TRAIN_AI","GENERATE_AI_CONTEXT"]
    source_assets: list[str] = Field(min_length=1)
    target: str | None = None
    state: GovernanceState
    metadata: dict[str, Any] = Field(default_factory=dict)

class RepairAction(BaseModel):
    type: str
    details: dict[str, Any] = Field(default_factory=dict)

class GovernanceCertificate(BaseModel):
    request_id: str
    actor: str
    operation: str
    source_assets: list[str]
    target: str | None
    pre_state: GovernanceState
    post_state: GovernanceState
    governance_delta: float
    decision: Decision
    reason_codes: list[str]
    repair_actions: list[RepairAction] = Field(default_factory=list)
    policy_version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    digest: str

class GovernanceResult(BaseModel):
    decision: Decision
    reason_codes: list[str]
    repair_actions: list[RepairAction]
    certificate: GovernanceCertificate
