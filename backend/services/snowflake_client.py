# backend/services/snowflake_client.py
"""
Snowflake client for RAG-like lookups of terms/lab ranges.
Env:
- SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT
- SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_WAREHOUSE
"""

from __future__ import annotations
import os
import snowflake.connector


def _connect():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER", "DAMIN05"),
        password=os.getenv("SNOWFLAKE_PASSWORD", "HackRU@snowflake05"),
        account=os.getenv("SNOWFLAKE_ACCOUNT", "PJSJKED-XQ33297"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "CLARIMED_DB"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
    )


def fetch_rag_snippets(candidate_terms: list[str]) -> str:
    """
    Fetch simple definitions for candidate terms from a MEDICAL_TERMS table:
      MEDICAL_TERMS(term VARCHAR, simple_definition VARCHAR)
    Returns a newline-joined string like:
      'term: definition\nterm2: definition2'
    Gracefully returns "" if nothing found or Snowflake unavailable.
    """
    terms = [
        t.lower().strip(" ,.:;()[]{}\"'") for t in (candidate_terms or []) if len(t or "") >= 3
    ]
    terms = list({t for t in terms})[:20]
    if not terms:
        return ""

    sql = "SELECT term, simple_definition FROM MEDICAL_TERMS WHERE "
    like_clauses = []
    params = []
    for t in terms:
        like_clauses.append("LOWER(term) LIKE %s")
        params.append(f"%{t}%")
    sql += " OR ".join(like_clauses)

    try:
        ctx = _connect()
        try:
            cs = ctx.cursor()
            try:
                cs.execute(sql, params)
                rows = cs.fetchall()
            finally:
                cs.close()
        finally:
            ctx.close()
    except Exception:
        # Non-fatal for hackathon flow
        return ""

    return "\n".join([f"{r[0]}: {r[1]}" for r in rows])