from __future__ import annotations
import json, os, sqlite3
from pathlib import Path
from typing import Any

class SQLiteCertificateStore:
    def __init__(self,path:str|None=None)->None:
        self.path=path or os.environ.get("DATAPROOF_DB_PATH","dataproof.db")
        if self.path!=":memory:": Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        self._memory_connection=None
        if self.path==":memory:":
            self._memory_connection=sqlite3.connect(":memory:",check_same_thread=False)
            self._memory_connection.row_factory=sqlite3.Row
        self._init_db()

    def _connect(self)->sqlite3.Connection:
        if self._memory_connection is not None: return self._memory_connection
        con=sqlite3.connect(self.path); con.row_factory=sqlite3.Row; return con

    def _init_db(self)->None:
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS certificates(
            request_id TEXT PRIMARY KEY, decision TEXT NOT NULL, digest TEXT NOT NULL,
            payload TEXT NOT NULL, created_at TEXT NOT NULL)""")

    def put(self,certificate:dict[str,Any])->None:
        payload=json.dumps(certificate,sort_keys=True,default=str)
        with self._connect() as con:
            con.execute("""INSERT INTO certificates(request_id,decision,digest,payload,created_at)
            VALUES(?,?,?,?,?) ON CONFLICT(request_id) DO UPDATE SET
            decision=excluded.decision,digest=excluded.digest,payload=excluded.payload,created_at=excluded.created_at""",
            (certificate["request_id"],certificate["decision"],certificate["digest"],payload,certificate["timestamp"]))

    def get(self,request_id:str)->dict[str,Any]|None:
        with self._connect() as con:
            row=con.execute("SELECT payload FROM certificates WHERE request_id=?",(request_id,)).fetchone()
        return json.loads(row["payload"]) if row else None

    def list(self,limit:int=100)->list[dict[str,Any]]:
        with self._connect() as con:
            rows=con.execute("SELECT payload FROM certificates ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
        return [json.loads(row["payload"]) for row in rows]
