from pathlib import Path
from dataproof.engine import GovernanceEngine
from dataproof.models import GovernanceRequest

def main():
    req=GovernanceRequest.model_validate_json(Path("examples/ai_overcollection.json").read_text(encoding="utf-8"))
    print(GovernanceEngine().evaluate(req).model_dump_json(indent=2))

if __name__=="__main__":
    main()
