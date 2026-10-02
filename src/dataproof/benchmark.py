from __future__ import annotations
import argparse,csv,json,time
from copy import deepcopy
from pathlib import Path
from .certificate import verify_certificate
from .engine import GovernanceEngine
from .models import GovernanceRequest
from .scenarios import SCENARIOS

def _ablate(item,mode):
    x=deepcopy(item)
    if mode=="no_purpose": x["state"]["purpose"]="billing"
    elif mode=="no_residency": x["state"]["region"]="us-east-1"
    elif mode=="no_quality": x["state"]["quality_score"]=1.0; x["state"]["age_hours"]=0
    elif mode=="no_lineage": x["state"]["lineage_complete"]=True
    elif mode=="no_composition": x["state"]["disclosure_risk"]=0.0; x["metadata"]["composition_risk"]=0.0
    elif mode=="no_minimization": x["state"]["required_fields"]=list(x["state"]["requested_fields"])
    elif mode=="no_policy_version": x["state"]["policy_version"]="v1.0.0"
    return x

def run(out:Path)->dict:
    out.mkdir(parents=True,exist_ok=True); engine=GovernanceEngine(); rows=[]
    for item in SCENARIOS:
        req=GovernanceRequest.model_validate({k:v for k,v in item.items() if k!="expected"})
        result=engine.evaluate(req)
        rows.append({"scenario":item["request_id"],"expected":item["expected"],"actual":result.decision.value,"pass":item["expected"]==result.decision.value,"reasons":"|".join(result.reason_codes),"digest":result.certificate.digest})
    with (out/"scenario_results.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    non_allow=[r for r in rows if r["expected"]!="ALLOW"]
    summary={"scenario_families":len(rows),"passed":sum(r["pass"] for r in rows),"policy_conformance":sum(r["pass"] for r in rows)/len(rows),"unrestricted_allow_errors":sum(r["actual"]=="ALLOW" for r in non_allow),"uaer":sum(r["actual"]=="ALLOW" for r in non_allow)/len(non_allow)}
    ablation={}
    for mode in ["no_purpose","no_residency","no_quality","no_lineage","no_composition","no_minimization","no_policy_version"]:
        correct=0
        for item in SCENARIOS:
            m=_ablate(item,mode); expected=item["expected"]
            req=GovernanceRequest.model_validate({k:v for k,v in m.items() if k!="expected"})
            correct+=engine.evaluate(req).decision.value==expected
        ablation[mode]={"passed":correct,"total":len(SCENARIOS),"conformance":correct/len(SCENARIOS)}
    detected=0
    for i in range(5000):
        base=SCENARIOS[0]
        req=GovernanceRequest.model_validate({k:v for k,v in base.items() if k!="expected"}).model_copy(update={"request_id":f"M{i}"})
        cert=engine.evaluate(req).certificate.model_dump(mode="json")
        cert["decision"]="DENY"
        detected+=not verify_certificate(cert)
    integrity={"tested":5000,"detected":detected,"rate":detected/5000}
    timings=[]
    for item in SCENARIOS:
        req=GovernanceRequest.model_validate({k:v for k,v in item.items() if k!="expected"})
        for _ in range(2000):
            t0=time.perf_counter_ns(); engine.evaluate(req); timings.append((time.perf_counter_ns()-t0)/1000.0)
    timings.sort()
    latency={"executions":len(timings),"mean_us":sum(timings)/len(timings),"p95_us":timings[int(.95*(len(timings)-1))],"p99_us":timings[int(.99*(len(timings)-1))]}
    report={"summary":summary,"ablation":ablation,"integrity":integrity,"latency":latency}
    (out/"summary.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    (out/"ablation.json").write_text(json.dumps(ablation,indent=2),encoding="utf-8")
    (out/"integrity.json").write_text(json.dumps(integrity,indent=2),encoding="utf-8")
    return report
def main():
    p=argparse.ArgumentParser(); p.add_argument("--out",type=Path,default=Path("artifacts/benchmark")); a=p.parse_args()
    print(json.dumps(run(a.out),indent=2))
if __name__=="__main__": main()
