from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any

DEFAULT_POLICY={
"policy_version":"v1.0.0",
"allowed_purposes":["billing","fraud_detection","customer_support","analytics","research"],
"allowed_regions":["us-east-1","us-east-2","us-west-2"],
"min_quality_score":0.80,
"max_age_hours":24,
"require_lineage_for":["JOIN","TRANSFORM","SHARE","EXPORT","TRAIN_AI","GENERATE_AI_CONTEXT"],
"composition_risk_threshold":0.70,
"review_on_stale_policy":True,
"deny_on_purpose_mismatch":True,
"deny_on_residency_violation":True,
"sensitive_classifications":["restricted","regulated"],
"policy_aliases":{}
}

def _repo_policy_path()->Path:
    return Path(__file__).resolve().parents[2]/"config"/"policy.json"

def load_policy(path:str|Path|None=None)->dict[str,Any]:
    configured=path or os.environ.get("DATAPROOF_POLICY_PATH")
    candidate=Path(configured) if configured else _repo_policy_path()
    if candidate.exists():
        data=json.loads(candidate.read_text(encoding="utf-8"))
        merged=dict(DEFAULT_POLICY); merged.update(data); return merged
    return dict(DEFAULT_POLICY)
