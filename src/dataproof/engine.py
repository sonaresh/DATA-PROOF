from __future__ import annotations
from copy import deepcopy
from typing import Any
from datetime import datetime, timezone

from .certificate import certificate_digest
from .models import Decision, GovernanceCertificate, GovernanceRequest, GovernanceResult, GovernanceState, RepairAction
from .policy import load_policy

SEVERITY={Decision.ALLOW:0,Decision.CONSTRAIN:1,Decision.REVIEW:2,Decision.DENY:3}

class GovernanceEngine:
    def __init__(self,policy:dict[str,Any]|None=None)->None:
        self.policy=policy or load_policy()

    def _candidate_state(self,req:GovernanceRequest)->GovernanceState:
        state=req.state.model_copy(deep=True); derived=req.metadata.get("derived",{})
        for field in ("classification","purpose","lineage_complete","quality_score","age_hours","region","disclosure_risk","requested_fields","required_fields","downstream","policy_version"):
            if field in derived: setattr(state,field,deepcopy(derived[field]))
        if req.operation in {"JOIN","TRANSFORM"}:
            state.disclosure_risk=max(state.disclosure_risk,float(req.metadata.get("composition_risk",state.disclosure_risk)))
        return state

    def _purpose_allowed(self,purpose:str)->bool:
        return purpose in set(self.policy["allowed_purposes"])

    def _decision(self,req:GovernanceRequest,post:GovernanceState):
        reasons=[]; repairs=[]; decision=Decision.ALLOW
        def raise_to(level,code):
            nonlocal decision
            reasons.append(code)
            if SEVERITY[level]>SEVERITY[decision]: decision=level
        if not req.role_authorized: raise_to(Decision.DENY,"SOURCE_AUTHORIZATION_FAILED")
        if not self._purpose_allowed(post.purpose):
            raise_to(Decision.DENY if self.policy.get("deny_on_purpose_mismatch",True) else Decision.REVIEW,"PURPOSE_MISMATCH")
        if post.region not in set(self.policy["allowed_regions"]):
            raise_to(Decision.DENY if self.policy.get("deny_on_residency_violation",True) else Decision.REVIEW,"RESIDENCY_VIOLATION")
        if req.operation in set(self.policy["require_lineage_for"]) and not post.lineage_complete:
            raise_to(Decision.REVIEW,"LINEAGE_INCOMPLETE")
        if post.quality_score<float(self.policy["min_quality_score"]): raise_to(Decision.REVIEW,"QUALITY_INSUFFICIENT")
        if post.age_hours>float(self.policy["max_age_hours"]): raise_to(Decision.REVIEW,"DATA_STALE")
        if self.policy.get("review_on_stale_policy",True) and post.policy_version!=self.policy["policy_version"]:
            raise_to(Decision.REVIEW,"POLICY_VERSION_STALE")
        if post.disclosure_risk>=float(self.policy["composition_risk_threshold"]):
            repairs.append(RepairAction(type="MASK_OR_TOKENIZE",details={"target_risk_below":self.policy["composition_risk_threshold"]}))
            raise_to(Decision.CONSTRAIN,"COMPOSITION_RISK")
        requested=list(dict.fromkeys(post.requested_fields)); required=set(post.required_fields)
        unnecessary=[f for f in requested if required and f not in required]
        if unnecessary:
            retain=[f for f in requested if f in required]
            repairs.append(RepairAction(type="REDUCE_FIELDS",details={"retain":retain,"remove":unnecessary}))
            raise_to(Decision.CONSTRAIN,"MINIMIZATION_REQUIRED")
        if decision is Decision.ALLOW and not reasons: reasons.append("POLICY_SATISFIED")
        return decision,reasons,repairs

    def evaluate(self,req:GovernanceRequest)->GovernanceResult:
        post=self._candidate_state(req)
        decision,reasons,repairs=self._decision(req,post)
        governance_delta=round(post.disclosure_risk-req.state.disclosure_risk,6)
        cert_data={
        "request_id":req.request_id,"actor":req.actor,"operation":req.operation,
        "source_assets":req.source_assets,"target":req.target,
        "pre_state":req.state.model_dump(mode="json"),"post_state":post.model_dump(mode="json"),
        "governance_delta":governance_delta,"decision":decision.value,"reason_codes":reasons,
        "repair_actions":[r.model_dump(mode="json") for r in repairs],
        "policy_version":self.policy["policy_version"],
        "timestamp":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
        cert_data["digest"]=certificate_digest(cert_data)
        certificate=GovernanceCertificate.model_validate(cert_data)
        return GovernanceResult(decision=decision,reason_codes=reasons,repair_actions=repairs,certificate=certificate)
