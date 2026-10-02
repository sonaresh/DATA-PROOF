from dataproof.engine import GovernanceEngine
from dataproof.models import GovernanceRequest
from dataproof.scenarios import SCENARIOS

def test_all_canonical_scenarios_match_expected():
    engine=GovernanceEngine()
    for item in SCENARIOS:
        expected=item["expected"]; payload={k:v for k,v in item.items() if k!="expected"}
        result=engine.evaluate(GovernanceRequest.model_validate(payload))
        assert result.decision.value==expected,item["request_id"]

def test_ai_overcollection_returns_field_reduction():
    item=next(x for x in SCENARIOS if x["request_id"]=="S7")
    result=GovernanceEngine().evaluate(GovernanceRequest.model_validate({k:v for k,v in item.items() if k!="expected"}))
    assert result.decision.value=="CONSTRAIN"
    action=next(x for x in result.repair_actions if x.type=="REDUCE_FIELDS")
    assert action.details["retain"]==["customer_id","invoice_total","payment_status"]
    assert "ssn" in action.details["remove"]

def test_sensitive_join_constrained():
    item=next(x for x in SCENARIOS if x["request_id"]=="S6")
    result=GovernanceEngine().evaluate(GovernanceRequest.model_validate({k:v for k,v in item.items() if k!="expected"}))
    assert result.decision.value=="CONSTRAIN"
    assert "COMPOSITION_RISK" in result.reason_codes
