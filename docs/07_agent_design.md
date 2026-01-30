# AI Agent Design: Natural Language Queries over Operational Data

This document outlines a conceptual design for a Generative AI agent that enables users to query operational support ticket data using natural language. For a record of prompt issues encountered and fixes applied, see [09_prompt_issues_and_fixes.md](09_prompt_issues_and_fixes.md).

The agent is designed to operate over data stored in Amazon S3 and queried via Amazon Athena.

---

## 1. User Interaction Example

Example user questions:
- "How many high priority tickets do we have?"
- "Which categories generate the most urgent tickets?"
- "What percentage of tickets are high priority?"

---

## 2. Agent Responsibilities

The AI agent is responsible for:
1. Interpreting the user's question
2. Generating a read-only SQL query dynamically (LLM) from the question and schema
3. Executing the query against Athena (with lightweight guardrails)
4. Summarizing the results in business-friendly language

The agent does not make operational decisions or modify data.

---

## 3. Query Mapping (Reasoning Step)

Example mapping:

**User Question:**  
"How many high priority tickets do we have?"

**Agent Reasoning:**  
- Identify metric: ticket count  
- Identify filter: priority = 'high'  
- Identify data source: ops_data.tickets  

**Generated Query:**
```sql
SELECT COUNT(*) AS high_priority_tickets
FROM ops_data.tickets
WHERE priority = 'high';
```

---

## 4. Current implementation

- **Agent retry**: The agent tries up to **MAX_SQL_RETRIES** (default 5) times to produce valid SQL and run it. Retries happen on (1) execution failure (guardrail error, Athena error, or no SELECT in output) and (2) when the query succeeds but returns **0 rows** (if `RETRY_ON_ZERO_ROWS` is true): the LLM is told to consider `LIKE 'value%'` for text filters (e.g. category) instead of exact match. This addresses cases where e.g. "IT tickets" returns 0 rows with `category = 'IT'` but would match with `category LIKE 'IT%'`.
- **SQL generation**: The LLM generates SQL dynamically from the question and a schema description (table and columns). The agent uses a dedicated SQL-generation prompt and extracts the SELECT statement from the model output (handles markdown code blocks). No fixed template set.
- **Execution**: The generated query is executed on Amazon Athena via `run_athena_query`. **Guardrails** (lightweight, enforce safety while keeping the agent flexible):
  - **Read-only**: Only SELECT queries are allowed; write/DDL keywords (INSERT, UPDATE, DELETE, DROP, CREATE, etc.) are rejected.
  - **Schema constraint**: Queries may only reference the allowed table(s) (e.g. `tickets` or `ops_data.tickets`); any other table reference raises an error.
- **Summarization**: After receiving the result rows, the agent calls an LLM with a summarization prompt (question + raw rows) and returns the model’s plain-language summary. Optionally, raw rows and the executed SQL can be included for audit.
- **Conversation context**: The CLI keeps the last N (question, answer) turns (default 2; `CONVERSATION_HISTORY_SIZE`) and passes them into the SQL-generation prompt so follow-up questions (e.g. "Break that down by category?") are resolved against the previous turn.
- **Manual SQL verification**: Set `SHOW_SQL=1` when running to print the executed SQL after each answer so you can run it in Athena and compare results when debugging.
- **Schema enrichment**: When `SCHEMA_ENRICHMENT` is on (default), the agent fetches distinct values for category, priority, ticket_type, and assigned_to from Athena (once per session) and adds them to the prompt as "Sample values from data". The LLM is told to use these exact values in filters when they match the user's intent (e.g. "IT" -> "IT Support"). This reduces wrong filters and 0-row results. If enrichment is off or fetch fails, the agent falls back to the base schema and may use `LIKE 'value%'` for short terms.
- **SQL guidance**: When sample values are provided, prefer exact values from that list; otherwise use `LIKE 'value%'` for short terms.
- **Config**: Athena database, table, and S3 output via `ATHENA_DATABASE`, `ATHENA_TABLE`, `ATHENA_OUTPUT`. Retry limit via `MAX_SQL_RETRIES` (default 5). Context size via `CONVERSATION_HISTORY_SIZE` (default 2). Retry on 0 rows via `RETRY_ON_ZERO_ROWS` (default true).

## 5. Next steps

- Optional: Audit log (e.g. question + SQL + timestamp) for auditability.
- Optional: Broader schema (multiple tables) with explicit allowlist.
- **Future / LangChain**: For more advanced behavior (e.g. an agent that decides whether to run a query, retry, or ask the user for clarification in a multi-step loop), consider transitioning to a LangChain agent with tools: expose `run_athena_query` as a tool and let the LLM choose when to call it and with what query. The current design keeps retries and 0-row logic in code to limit LLM calls and cost; a full LangChain agent would be more flexible but use more tokens per turn.

