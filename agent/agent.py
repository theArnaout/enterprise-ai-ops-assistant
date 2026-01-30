import re

from langchain_openai import ChatOpenAI

from .tools import run_athena_query
from .config import (
    ATHENA_DATABASE,
    MAX_SQL_RETRIES,
    RETRY_ON_ZERO_ROWS,
    SCHEMA_ENRICHMENT,
    SCHEMA_ENRICHMENT_COLUMNS,
    SCHEMA_ENRICHMENT_MAX_VALUES,
)
from .prompts import (
    SCHEMA_DESCRIPTION,
    SQL_GENERATION_PROMPT,
    SQL_GENERATION_RETRY_PROMPT,
    SUMMARIZE_RESULTS_PROMPT,
)

# Cache for distinct column values (filled on first use when schema enrichment is on)
_SCHEMA_VALUES_CACHE: dict[str, list[str]] | None = None


def _format_conversation_context(history: list[tuple[str, str]] | None) -> str:
    """Format last N (question, answer) turns for the prompt."""
    if not history:
        return "No previous conversation."
    lines = []
    for q, a in history:
        lines.append(f"- User: {q}")
        lines.append(f"- Assistant: {a}")
    return "\n".join(lines)

llm = ChatOpenAI(temperature=0)


def _extract_sql(text: str) -> str:
    """
    Extract a single SELECT statement from LLM output.
    Handles markdown code blocks and trims to the first SELECT ... statement.
    """
    t = text.strip()
    # Remove markdown code block if present
    if "```" in t:
        match = re.search(r"```(?:sql)?\s*(.*?)\s*```", t, re.DOTALL | re.IGNORECASE)
        if match:
            t = match.group(1).strip()
    # Find start of SELECT
    start = re.search(r"\bselect\b", t, re.IGNORECASE)
    if not start:
        raise ValueError("No SELECT statement found in model output.")
    t = t[start.start() :].strip()
    # Take up to first semicolon or end
    if ";" in t:
        t = t.split(";", 1)[0].strip()
    return t


def _format_rows_for_prompt(rows: list) -> str:
    """Format Athena result rows as a string for the LLM."""
    if not rows:
        return "(No rows returned.)"
    return "\n".join(str(row) for row in rows)


def _is_zero_data_rows(rows: list) -> bool:
    """True when Athena returned 0 data rows (empty list or only header row)."""
    if len(rows) == 0:
        return True
    if len(rows) == 1 and rows[0].get("Data"):
        first_cell = (rows[0]["Data"][0] or {}).get("VarCharValue", "")
        if first_cell == "ticket_id":
            return True
    return False


def _parse_distinct_rows(rows: list, column_name: str) -> list[str]:
    """Parse Athena result rows for a single-column SELECT DISTINCT; skip header; return values."""
    values = []
    for i, row in enumerate(rows):
        if not row.get("Data") or not row["Data"]:
            continue
        cell = (row["Data"][0] or {}).get("VarCharValue", "").strip()
        if not cell:
            continue
        if i == 0 and cell.lower() == column_name.lower():
            continue
        values.append(cell)
        if len(values) >= SCHEMA_ENRICHMENT_MAX_VALUES:
            break
    return values


def _fetch_distinct_values(column: str) -> list[str] | None:
    """Run SELECT DISTINCT column FROM tickets and return list of values, or None on failure."""
    if column not in SCHEMA_ENRICHMENT_COLUMNS:
        return None
    try:
        q = f"SELECT DISTINCT {column} FROM tickets LIMIT {SCHEMA_ENRICHMENT_MAX_VALUES + 10}"
        rows = run_athena_query(q)
        return _parse_distinct_rows(rows, column)
    except (ValueError, RuntimeError):
        return None


def _get_enriched_schema() -> str:
    """Return schema description with sample distinct values when enrichment is on (so LLM uses exact names)."""
    global _SCHEMA_VALUES_CACHE
    if not SCHEMA_ENRICHMENT:
        return SCHEMA_DESCRIPTION
    if _SCHEMA_VALUES_CACHE is None:
        cache: dict[str, list[str]] = {}
        for col in SCHEMA_ENRICHMENT_COLUMNS:
            vals = _fetch_distinct_values(col)
            if vals:
                cache[col] = vals
        _SCHEMA_VALUES_CACHE = cache
    if not _SCHEMA_VALUES_CACHE:
        return SCHEMA_DESCRIPTION
    lines = [
        SCHEMA_DESCRIPTION.strip(),
        "",
        "Sample values from data (use these exact values in filters when they match the user's intent):",
    ]
    for col, vals in _SCHEMA_VALUES_CACHE.items():
        lines.append(f"- {col}: " + ", ".join(repr(v) for v in vals[:20]))
        if len(vals) > 20:
            lines.append(f"  (and {len(vals) - 20} more)")
    return "\n".join(lines)


def ask_agent(
    question: str,
    include_raw_rows: bool = False,
    return_sql: bool = False,
    conversation_history: list[tuple[str, str]] | None = None,
):
    """
    Agent: generate SQL from the question via LLM, run on Athena (with guardrails), retry on failure.
    Up to MAX_SQL_RETRIES attempts; on each failure the LLM receives the error and produces a corrected query.
    Then summarize results in one LLM call and return to the user.
    conversation_history: list of (user_question, agent_summary) for the last N turns (enables follow-up questions).
    return_sql: if True, return a dict with summary and sql so the caller can print SQL for manual verification.
    Guardrails: read-only queries only; schema constraint (allowed table(s) only).
    """
    conversation_context = _format_conversation_context(conversation_history or [])
    schema = _get_enriched_schema()
    sql = None
    last_error = None
    for attempt in range(MAX_SQL_RETRIES):
        try:
            if attempt == 0:
                prompt = SQL_GENERATION_PROMPT.format(
                    schema=schema,
                    database=ATHENA_DATABASE,
                    question=question,
                    conversation_context=conversation_context,
                )
            else:
                prompt = SQL_GENERATION_RETRY_PROMPT.format(
                    schema=schema,
                    database=ATHENA_DATABASE,
                    question=question,
                    conversation_context=conversation_context,
                    previous_sql=sql or "(none)",
                    error=last_error or "(unknown)",
                )
            raw_sql = llm.invoke(prompt).content
            sql = _extract_sql(raw_sql)
            rows = run_athena_query(sql)
            # Retry when query succeeded but returned 0 data rows (empty or only Athena header row)
            if RETRY_ON_ZERO_ROWS and _is_zero_data_rows(rows) and attempt < MAX_SQL_RETRIES - 1:
                last_error = (
                    "Query succeeded but returned 0 rows. Consider using LIKE 'value%' for text columns "
                    "(e.g. category LIKE 'IT%') instead of exact = 'value', or check that filter values match the data."
                )
                continue
            break
        except (ValueError, RuntimeError) as e:
            last_error = str(e)
            if attempt == MAX_SQL_RETRIES - 1:
                raise RuntimeError(
                    f"Could not generate valid SQL after {MAX_SQL_RETRIES} attempts. Last error: {last_error}"
                ) from e
    results_str = _format_rows_for_prompt(rows)
    summarizer_prompt = SUMMARIZE_RESULTS_PROMPT.format(
        question=question,
        results=results_str,
    )
    summary = llm.invoke(summarizer_prompt).content
    if include_raw_rows:
        return {"summary": summary, "raw_rows": rows, "sql": sql}
    if return_sql:
        return {"summary": summary, "sql": sql}
    return summary

