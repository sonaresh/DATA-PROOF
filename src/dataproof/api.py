from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException, Query
from .certificate import verify_certificate
from .engine import GovernanceEngine
from .models import GovernanceRequest, GovernanceResult
from .storage import SQLiteCertificateStore

app=FastAPI(title="DATA-PROOF",version="0.1.0",description="Runtime governance-state assurance for data transformation and AI consumption.")
engine=GovernanceEngine()
store=SQLiteCertificateStore()

@app.get("/health")
def health()->dict:
    return {"status":"ok","policy_version":engine.policy["policy_version"]}

@app.post("/v1/evaluate",response_model=GovernanceResult)
def evaluate(req:GovernanceRequest)->GovernanceResult:
    result=engine.evaluate(req); store.put(result.certificate.model_dump(mode="json")); return result

@app.get("/v1/certificates")
def list_certificates(limit:int=Query(default=100,ge=1,le=1000))->list[dict]:
    return store.list(limit=limit)

@app.get("/v1/certificates/{request_id}")
def get_certificate(request_id:str)->dict:
    cert=store.get(request_id)
    if not cert: raise HTTPException(status_code=404,detail="certificate not found")
    return cert

@app.get("/v1/certificates/{request_id}/verify")
def verify_stored_certificate(request_id:str)->dict:
    cert=store.get(request_id)
    if not cert: raise HTTPException(status_code=404,detail="certificate not found")
    return {"request_id":request_id,"valid":verify_certificate(cert),"digest":cert["digest"]}

def run()->None:
    import uvicorn
    uvicorn.run("dataproof.api:app",host=os.environ.get("DATAPROOF_HOST","0.0.0.0"),port=int(os.environ.get("DATAPROOF_PORT","8000")),reload=False)
