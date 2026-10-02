from __future__ import annotations
import hashlib, json
from typing import Any

def canonical_payload(data:dict[str,Any])->bytes:
    body=dict(data); body.pop("digest",None)
    return json.dumps(body,sort_keys=True,separators=(",",":"),default=str).encode("utf-8")

def certificate_digest(data:dict[str,Any])->str:
    return hashlib.sha256(canonical_payload(data)).hexdigest()

def verify_certificate(data:dict[str,Any])->bool:
    digest=data.get("digest")
    return isinstance(digest,str) and digest==certificate_digest(data)
