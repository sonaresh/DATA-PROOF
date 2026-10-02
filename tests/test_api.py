import os
os.environ["DATAPROOF_DB_PATH"]=":memory:"
from fastapi.testclient import TestClient
from dataproof.api import app
from dataproof.scenarios import SCENARIOS
client=TestClient(app)

def test_health():
    r=client.get("/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_evaluate_persist_and_verify():
    payload={k:v for k,v in SCENARIOS[6].items() if k!="expected"}
    r=client.post("/v1/evaluate",json=payload)
    assert r.status_code==200
    assert r.json()["decision"]=="CONSTRAIN"
    rid=payload["request_id"]
    assert client.get(f"/v1/certificates/{rid}").status_code==200
    verify=client.get(f"/v1/certificates/{rid}/verify")
    assert verify.status_code==200
    assert verify.json()["valid"] is True
