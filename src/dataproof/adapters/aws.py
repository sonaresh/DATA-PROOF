from __future__ import annotations
from typing import Any

class AWSMetadataAdapter:
    """Read governance metadata using the standard boto3 credential provider chain."""
    def __init__(self,session=None):
        try: import boto3
        except ImportError as exc: raise RuntimeError("Install DATA-PROOF with the aws extra: pip install -e '.[aws]'") from exc
        self.session=session or boto3.Session()
        self.s3=self.session.client("s3"); self.glue=self.session.client("glue")
    def s3_object_tags(self,bucket:str,key:str)->dict[str,str]:
        response=self.s3.get_object_tagging(Bucket=bucket,Key=key)
        return {x["Key"]:x["Value"] for x in response.get("TagSet",[])}
    def glue_table_parameters(self,database:str,table:str)->dict[str,Any]:
        response=self.glue.get_table(DatabaseName=database,Name=table)
        return dict(response["Table"].get("Parameters",{}))
