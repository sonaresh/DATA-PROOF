from __future__ import annotations
from copy import deepcopy
BASE={"actor":"analyst@example.com","role_authorized":True,"operation":"READ","source_assets":["customer"],
"state":{"classification":"internal","purpose":"billing","lineage_complete":True,"quality_score":0.95,"age_hours":2,"region":"us-east-1","disclosure_risk":0.20,"requested_fields":[],"required_fields":[],"downstream":"internal","policy_version":"v1.0.0"},"metadata":{}}
def scenario(request_id:str,expected:str,**changes):
    x=deepcopy(BASE); x["request_id"]=request_id; x["expected"]=expected
    for path,value in changes.items():
        if path.startswith("state__"): x["state"][path.split("__",1)[1]]=value
        elif path.startswith("metadata__"): x["metadata"][path.split("__",1)[1]]=value
        else: x[path]=value
    return x
SCENARIOS=[
scenario("S1","ALLOW"),
scenario("S2","DENY",state__purpose="unapproved_marketing",operation="EXPORT"),
scenario("S3","DENY",state__region="eu-west-1",operation="EXPORT"),
scenario("S4","REVIEW",state__quality_score=0.50,operation="TRANSFORM"),
scenario("S5","REVIEW",state__lineage_complete=False,operation="JOIN"),
scenario("S6","CONSTRAIN",operation="JOIN",metadata__composition_risk=0.91),
scenario("S7","CONSTRAIN",operation="GENERATE_AI_CONTEXT",state__requested_fields=["customer_id","invoice_total","payment_status","ssn","dob","address","medical_notes","email","phone","zipcode"],state__required_fields=["customer_id","invoice_total","payment_status"]),
scenario("S8","DENY",operation="TRAIN_AI",state__purpose="model_training_unapproved"),
scenario("S9","ALLOW",operation="JOIN",metadata__composition_risk=0.30),
scenario("S10","REVIEW",operation="TRANSFORM",state__quality_score=0.70),
scenario("S11","DENY",operation="SHARE",state__region="ap-south-1"),
scenario("S12","REVIEW",operation="TRANSFORM",state__policy_version="v0.9.0"),
scenario("S13","CONSTRAIN",operation="EXPORT",state__disclosure_risk=0.85,state__requested_fields=["customer_id","ssn"],state__required_fields=["customer_id"]),
scenario("S14","ALLOW",operation="TRANSFORM",state__disclosure_risk=0.10),
scenario("S15","DENY",role_authorized=False),
scenario("S16","DENY",operation="TRAIN_AI",state__purpose="external_finetuning")]
