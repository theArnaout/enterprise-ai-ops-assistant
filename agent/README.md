# Agent — AI-Assisted Analytics Query Agent

The agent answers natural-language questions about operational support ticket data by **generating SQL dynamically** with an LLM, executing queries on Amazon Athena (with lightweight guardrails), and summarizing results in plain language.

## Purpose

- Accept questions such as “How many high priority tickets do we have?” or “Which categories have the most high-priority tickets?”
- Generate read-only SQL from the question and schema (LLM); no fixed template set.
- Run queries against Athena (data in S3) with **guardrails**: read-only only, schema constraint (allowed table(s) only).
- **Retry on failure**: up to 5 attempts (configurable via `MAX_SQL_RETRIES`); on each failure the LLM receives the error and produces a corrected query, then one summarization call returns the result to the user.
- **Conversation context**: the last N (question, answer) turns (default 2; `CONVERSATION_HISTORY_SIZE`) are passed into the agent so follow-ups like “Break that down by category?” work without rephrasing.
- **Schema enrichment** (default on): distinct values for category, priority, ticket_type, and assigned_to are fetched from Athena once per session and added to the prompt so the LLM uses exact names (e.g. "IT Support") instead of guessing; reduces wrong filters and 0-row results.
- Return a short, data-backed summary in plain language.
- **Manual SQL verification**: set `SHOW_SQL=1` when running to print the executed SQL after each answer so you can run it in Athena and compare results.

## Prerequisites

- **Python 3.x** (3.10+ recommended)
- **AWS credentials** configured (e.g. `~/.aws/credentials` or env vars) with permission to run Athena queries and write to the S3 output location
- **OpenAI API key** for LLM summarization
- **Athena database and table**: e.g. `ops_data.tickets` created and pointing at your ticket data in S3
- **S3 bucket** for Athena query results (output location)

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for SQL generation and summarization |
| `ATHENA_DATABASE` | No | Athena database name (default: `ops_data`) |
| `ATHENA_TABLE` | No | Allowed table name for schema guardrail (default: `tickets`) |
| `ATHENA_OUTPUT` | No | S3 URI for Athena results, e.g. `s3://your-bucket/athena-results/` (default: project-specific bucket) |
| `MAX_SQL_RETRIES` | No | Max attempts to generate and run valid SQL before returning an error (default: `5`) |
| `CONVERSATION_HISTORY_SIZE` | No | Number of previous (question, answer) turns for context (default: `2`) |
| `SHOW_SQL` | No | Set to `1`, `true`, or `yes` to print the executed SQL after each answer (for manual verification) |
| `RETRY_ON_ZERO_ROWS` | No | When `true` (default), retry SQL generation if the query returns 0 rows (suggests LIKE for text filters). Set to `false` to disable |
| `SCHEMA_ENRICHMENT` | No | When `true` (default), fetch distinct values for category, priority, ticket_type, assigned_to from Athena (once per session) and add to prompt so the LLM uses exact names. Set to `false` to skip |
| `SCHEMA_ENRICHMENT_COLUMNS` | No | Comma-separated columns to enrich; default `category,priority,ticket_type,assigned_to` |
| `SCHEMA_ENRICHMENT_MAX_VALUES` | No | Max distinct values per column to include; default `50` |

## How to run

From the **project root** (parent of `agent/`):

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
# Optional:
# export ATHENA_DATABASE=ops_data
# export ATHENA_OUTPUT=s3://your-bucket/athena-results/
python -m agent.run
```

Then type a question when prompted; type `exit` or `quit` to stop.

## Example questions

Any question answerable from the ticket schema (ticket_id, ticket_type, priority, category, assigned_to, description), for example:

- “How many tickets do we have?” / “Total tickets”
- “Breakdown by priority” / “Tickets by priority”
- “High priority by category” / “Which categories have the most high-priority tickets?”
- “Tickets by owner” / “Who is assigned the most tickets?” / “Team workload”
- “How many tickets per category?” / “Top 5 categories by ticket count”

The LLM generates the SQL; guardrails ensure read-only queries and only the allowed table(s).

## Design and implementation

- **Design**: [docs/07_agent_design.md](../docs/07_agent_design.md)
- **How-to and FAQs**: [docs/08_how_to_run_agent.md](../docs/08_how_to_run_agent.md)
