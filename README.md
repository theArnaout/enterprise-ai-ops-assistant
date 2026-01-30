# Enterprise AI Ops Assistant

A prototype enterprise AI assistant designed to support internal operational workflows through data validation, analytics, and human-in-the-loop decision support.

## Project goal

This project implements an **AI-assisted analytics query agent** that lets users ask natural-language questions about operational support ticket data and receive data-backed answers. The agent translates business questions into SQL queries executed on Amazon Athena, retrieves results from a structured dataset stored in S3, and summarizes those results in plain language using an LLM. The focus is on demonstrating how AI can be integrated into real data systems responsibly — including query execution, cloud integration, error handling, and documentation — in a way that mirrors enterprise analytics and enablement workflows. While the agent is a prototype, it highlights practical considerations such as guardrails, auditability, and data integrity that matter when applying AI in business and regulated environments.

## Key capabilities

- SQL-based data exploration and validation
- Serverless analytics using AWS Athena
- Operational dashboards with Power BI
- AI-assisted explanations and plain-language summaries
- Clear human review and decision ownership

## Skills demonstrated

This repository serves as a portfolio piece for the Data & AI Solutions role, demonstrating:

- **SQL and data profiling**: LLM-generated SQL with schema-aware guardrails, data documentation, and read-only enforcement
- **AWS (S3, Athena)**: Serverless query execution and S3-backed data
- **Python agent prototype**: Keyword-based routing, Athena integration, and LLM summarization
- **Documentation and enablement**: Project charter, architecture, requirements, how-to guides, and agent design
- **Agile-style delivery**: Phased plan, user stories, and documentation alongside implementation

## Project structure

- **`agent/`** — AI agent: natural-language routing, Athena execution, LLM summarization
- **`data/`** — Raw and processed ticket data (e.g. Parquet); dataset documentation
- **`sql/`** — Data profiling and operational metrics queries for Athena
- **`docs/`** — Charter, architecture, requirements, delivery plan, risks, data insights, agent design, how-to
- **`app/`** — Streamlit demo: chat with the agent and view ticket charts (see [app/README.md](app/README.md))
- **`dashboards/`** — Planned: Power BI / lightweight dashboards (Phase 2)
- **`apps/`** — Planned: Power Apps / automation (future)

## Setup and run (everything needed to run the agent)

### Prerequisites

- **Python 3.x** (3.10+ recommended)
- **AWS account** (for S3 and Athena)
- **OpenAI API key** (for the LLM)

### 1. Get the dataset

The agent expects a **tickets** table with columns: `ticket_id`, `ticket_type`, `priority`, `category`, `assigned_to`, `description` (see [data/README.md](data/README.md)).

**Option A — Use the included data (recommended for a quick run)**

- The repo includes processed Parquet: **`data/processed/tickets.parquet`**. Use this for upload to S3 (step 2).
- If you prefer to regenerate from raw CSV: the repo has **`data/raw/tickets_original.csv`**. In [notebooks/01_clean_and_convert_to_parquet.ipynb](notebooks/01_clean_and_convert_to_parquet.ipynb) set `INPUT_FILE = "data/raw/tickets_original.csv"` (or copy the file to `data/raw/tickets.csv`), run the notebook, then use the produced Parquet in `data/processed/` for upload.

**Option B — Use your own data**

- Provide a CSV with the same columns (`ticket_id`, `ticket_type`, `priority`, `category`, `assigned_to`, `description`). Run the notebook with that path, then upload the resulting Parquet to S3.

### 2. AWS: S3 and Athena

1. **Create an S3 bucket** (e.g. `my-ai-ops-bucket`).
2. **Upload the Parquet file** to a prefix, e.g. `s3://my-ai-ops-bucket/data/tickets/`.  
   - One file: upload `data/processed/tickets.parquet` to that prefix (e.g. `data/tickets/tickets.parquet`).  
   - AWS CLI example: `aws s3 cp data/processed/tickets.parquet s3://my-ai-ops-bucket/data/tickets/`
3. **Create a second S3 location for Athena query results** (e.g. `s3://my-ai-ops-bucket/athena-results/`). Athena will write query outputs here.
4. **Create the Athena database and table** in the AWS Athena console (or CLI), in the same region you will use for queries:
   - Create database: `CREATE DATABASE IF NOT EXISTS ops_data;`
   - Create external table (replace the S3 path with your bucket and prefix):

   ```sql
   CREATE EXTERNAL TABLE IF NOT EXISTS ops_data.tickets (
     ticket_id string,
     ticket_type string,
     priority string,
     category string,
     assigned_to string,
     description string
   )
   STORED AS PARQUET
   LOCATION 's3://my-ai-ops-bucket/data/tickets/';
   ```

5. **Configure AWS credentials** (e.g. `aws configure`, or `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`) so the agent can call Athena and read/write the result location.

### 3. Environment variables

From the **project root**:

```bash
# Required for the LLM
export OPENAI_API_KEY=your_openai_key

# Athena (use your bucket and paths from step 2)
export ATHENA_DATABASE=ops_data
export ATHENA_OUTPUT=s3://my-ai-ops-bucket/athena-results/
```

Optional: `ATHENA_TABLE`, `MAX_SQL_RETRIES`, `SHOW_SQL`, `CONVERSATION_HISTORY_SIZE`, `RETRY_ON_ZERO_ROWS`, `SCHEMA_ENRICHMENT`, etc. — see [agent/README.md](agent/README.md) and [docs/08_how_to_run_agent.md](docs/08_how_to_run_agent.md).

### 4. Install and run

**CLI:** `pip install -r requirements.txt` then `python -m agent.run`.

**Streamlit demo:** `pip install -r requirements.txt` then `streamlit run app/streamlit_app.py` — Chat tab for questions, Charts tab for ticket overview.

Type a natural-language question when prompted (e.g. “How many high priority IT tickets are there?”); type `exit` or `quit` to stop. For a browser UI, run `streamlit run app/streamlit_app.py` (see [app/README.md](app/README.md)). See [docs/08_how_to_run_agent.md](docs/08_how_to_run_agent.md) for more options and example questions.

---

## Dataset and schema: is anything hardcoded?

- **The data is not hardcoded.** You upload your own Parquet to S3 and point Athena at it. The repo includes sample data (`data/processed/tickets.parquet` and `data/raw/tickets_original.csv`) so you can run the agent without finding an external dataset.
- **The schema (table and columns) is fixed in the agent.** The code and prompts expect a table named **`tickets`** (configurable via `ATHENA_TABLE`) with columns **`ticket_id`, `ticket_type`, `priority`, `category`, `assigned_to`, `description`**. If your data matches this schema, no code changes are needed.
- **To use a different table or column set** you would need to: (1) update the schema description and rules in [agent/prompts.py](agent/prompts.py) (`SCHEMA_DESCRIPTION` and any column lists), (2) set `ATHENA_TABLE` and optionally `SCHEMA_ENRICHMENT_COLUMNS` in [agent/config.py](agent/config.py) or via env vars, and (3) ensure the guardrails in [agent/tools.py](agent/tools.py) (allowed table refs) still match. For this portfolio project, using the provided ticket schema is enough; the README documents the expected schema so reviewers know what the agent assumes.

## Delivery approach

The project follows a hybrid Agile approach, with defined phases, clear scope boundaries, and documentation created alongside implementation.

## Disclaimer

This project is a learning-focused prototype and does not automate decisions or approvals.
