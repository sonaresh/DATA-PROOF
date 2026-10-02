from dataproof.certificate import verify_certificate
from dataproof.engine import GovernanceEngine
from dataproof.models import GovernanceRequest
from dataproof.scenarios import SCENARIOS

def test_certificate_verifies_and_mutation_fails():
    payload={k:v for k,v in SCENARIOS[0].items() if k!="expected"}
    cert=GovernanceEngine().evaluate(GovernanceRequest.model_validate(payload)).certificate.model_dump(mode="json")
    assert verify_certificate(cert)
    cert["decision"]="DENY"
    assert not verify_certificate(cert)
