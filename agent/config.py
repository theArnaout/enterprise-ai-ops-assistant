import os

ATHENA_DATABASE = os.environ.get("ATHENA_DATABASE", "ops_data")
ATHENA_OUTPUT = os.environ.get(
    "ATHENA_OUTPUT",
    "s3://enterprise-ai-ops-assistant-arnaout-data/athena-results/",
)
ATHENA_TABLE = os.environ.get("ATHENA_TABLE", "tickets")

# Agent: max attempts to generate and run valid SQL before returning an error
MAX_SQL_RETRIES = int(os.environ.get("MAX_SQL_RETRIES", "5"))

# Conversation: number of previous (question, answer) turns to include for context
CONVERSATION_HISTORY_SIZE = int(os.environ.get("CONVERSATION_HISTORY_SIZE", "2"))

# Agent: when True, retry SQL generation if the query succeeds but returns 0 rows (suggests wrong filter, e.g. exact match instead of LIKE)
RETRY_ON_ZERO_ROWS = os.environ.get("RETRY_ON_ZERO_ROWS", "true").strip().lower() in ("true", "1", "yes")

# Schema enrichment: fetch distinct values for these columns from Athena and add to prompt (so LLM uses exact names)
SCHEMA_ENRICHMENT = os.environ.get("SCHEMA_ENRICHMENT", "true").strip().lower() in ("true", "1", "yes")
SCHEMA_ENRICHMENT_COLUMNS = [
    c.strip() for c in os.environ.get("SCHEMA_ENRICHMENT_COLUMNS", "category,priority,ticket_type,assigned_to").split(",")
    if c.strip()
]
SCHEMA_ENRICHMENT_MAX_VALUES = int(os.environ.get("SCHEMA_ENRICHMENT_MAX_VALUES", "50"))

# Allowed table references for schema guardrail (database.table or table only)
ALLOWED_TABLE_REFS = (f"{ATHENA_DATABASE}.{ATHENA_TABLE}", ATHENA_TABLE)

SQL_TEMPLATES = {
    "total_tickets": """
        SELECT COUNT(*) AS total_tickets
        FROM ops_data.tickets;
    """,

    "tickets_by_priority": """
        SELECT
          priority,
          COUNT(*) AS ticket_count
        FROM ops_data.tickets
        GROUP BY priority
        ORDER BY ticket_count DESC;
    """,

    "tickets_by_category": """
        SELECT
          category,
          COUNT(*) AS ticket_count
        FROM ops_data.tickets
        GROUP BY category
        ORDER BY ticket_count DESC;
    """,

    "high_priority_by_category": """
        SELECT
          category,
          COUNT(*) AS high_priority_tickets
        FROM ops_data.tickets
        WHERE priority = 'high'
        GROUP BY category
        ORDER BY high_priority_tickets DESC;
    """,

    "tickets_by_owner": """
        SELECT
          assigned_to,
          COUNT(*) AS ticket_count
        FROM ops_data.tickets
        GROUP BY assigned_to
        ORDER BY ticket_count DESC;
    """
}

