import boto3
import re
import time

from .config import ATHENA_DATABASE, ATHENA_OUTPUT, ALLOWED_TABLE_REFS

client = boto3.client("athena")


def _validate_schema_constraint(query: str) -> None:
    """
    Ensures the query only references allowed table(s).
    Raises ValueError if any other table is referenced.
    """
    # Normalize: lowercase, collapse whitespace for parsing
    q = " " + query.strip().lower() + " "
    # Find table references after FROM and JOIN (simple heuristic)
    # Matches: from <table>, join <table> (with optional schema prefix)
    pattern = r"\b(?:from|join)\s+([a-z0-9_]+(?:\.[a-z0-9_]+)?)\b"
    refs = re.findall(pattern, q)
    allowed_lower = {ref.lower() for ref in ALLOWED_TABLE_REFS}
    for ref in refs:
        if ref not in allowed_lower:
            raise ValueError(
                f"Schema constraint: only table(s) {ALLOWED_TABLE_REFS} are allowed. "
                f"Query references: {ref!r}."
            )


# Read-only guardrail: reject queries containing write/ddl keywords
_READONLY_FORBIDDEN = (
    "insert", "update", "delete", "drop", "create", "alter", "truncate",
    "replace", "merge", "grant", "revoke",
)


def run_athena_query(query: str) -> list:
    """
    Executes a read-only Athena query and returns the result rows.
    Guardrails:
    - SELECT queries only (and no write/DDL keywords elsewhere)
    - Only allowed table(s) may be referenced (schema constraint)
    """
    q = query.strip()
    if not q.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    q_lower = q.lower()
    for kw in _READONLY_FORBIDDEN:
        if re.search(rf"\b{re.escape(kw)}\b", q_lower):
            raise ValueError(f"Read-only guardrail: keyword '{kw}' is not allowed.")
    _validate_schema_constraint(q)

    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )

    execution_id = response["QueryExecutionId"]

    # Wait for completion
    while True:
        status = client.get_query_execution(
            QueryExecutionId=execution_id
        )["QueryExecution"]["Status"]["State"]

        if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break

        time.sleep(1)

    if status != "SUCCEEDED":
        raise RuntimeError(f"Athena query failed: {status}")

    results = client.get_query_results(QueryExecutionId=execution_id)
    return results["ResultSet"]["Rows"]

