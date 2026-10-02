from __future__ import annotations
import argparse, json
from pathlib import Path
from .certificate import verify_certificate
from .engine import GovernanceEngine
from .models import GovernanceRequest

def main()->None:
    parser=argparse.ArgumentParser(prog="dataproof")
    sub=parser.add_subparsers(dest="command",required=True)
    ev=sub.add_parser("evaluate"); ev.add_argument("request",type=Path)
    vr=sub.add_parser("verify"); vr.add_argument("certificate",type=Path)
    args=parser.parse_args()
    if args.command=="evaluate":
        req=GovernanceRequest.model_validate_json(args.request.read_text(encoding="utf-8"))
        print(GovernanceEngine().evaluate(req).model_dump_json(indent=2))
    else:
        data=json.loads(args.certificate.read_text(encoding="utf-8"))
        print(json.dumps({"valid":verify_certificate(data),"digest":data.get("digest")},indent=2))
if __name__=="__main__": main()
