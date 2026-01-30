SYSTEM_PROMPT = """
You are an internal analytics assistant for support ticket analytics.
You generate read-only SQL (SELECT only) against the allowed schema.
You must only reference the table(s) and columns described in the schema.
If a question is outside scope or cannot be answered from the data, say so.
"""

# Schema description for SQL generation (table and columns)
SCHEMA_DESCRIPTION = """
Table: tickets (support ticket data)
Columns:
- ticket_id: unique identifier
- ticket_type: e.g. Request, Incident, Change
- priority: e.g. high, medium, low
- category: functional category or routing group (e.g. "IT Support", "Technical Support")
- assigned_to: team or person responsible for the ticket (e.g. "IT Services")
- description: free-text description of the issue

Terminology: In this dataset, "IT tickets" means tickets assigned to IT (filter on assigned_to, e.g. assigned_to = 'IT Services'), not tickets whose category is "IT Support" or "Technical Support". Use assigned_to when the user asks about IT tickets, tickets for IT, etc.
When sample values are provided below, prefer exact values from that list in filters. If no sample values are given, use LIKE 'term%%' for short terms.
"""

SQL_GENERATION_PROMPT = """You generate a single read-only SQL (SELECT) query for Amazon Athena.

{schema}

Rules:
- Use only the table and columns above. Table name: tickets (or {database}.tickets).
- Return only the SQL query, no explanation. No markdown, no code block wrapper.
- Use valid Athena SQL (e.g. no semicolon required).
- "IT tickets" means tickets assigned to IT: filter on assigned_to (e.g. assigned_to = 'IT Services' or assigned_to LIKE 'IT%%'), not on category.
- For other text filters: use exact values from the sample list when provided, or LIKE 'value%%' for short terms; use exact = when the exact value is known.
- If the user's question refers to "that", "same", "it", "above", or similar, use the previous conversation context to resolve what they mean.

Previous conversation (for context):
{conversation_context}

Current user question: {question}
"""

# Used when a previous SQL attempt failed (guardrail or Athena error); ask for a corrected query
SQL_GENERATION_RETRY_PROMPT = """You generate a single read-only SQL (SELECT) query for Amazon Athena.

{schema}

Rules:
- Use only the table and columns above. Table name: tickets (or {database}.tickets).
- Return only the SQL query, no explanation. No markdown, no code block wrapper.
- Use valid Athena SQL (e.g. no semicolon required).

The previous attempt failed. Fix the query based on the error below.

Previous conversation (for context):
{conversation_context}

Current user question: {question}

Previous SQL (failed):
{previous_sql}

Error from system:
{error}

If the error says "returned 0 rows", check the filter: "IT tickets" means assigned_to (e.g. assigned_to = 'IT Services'), not category. Use LIKE 'value%%' or exact values from the sample list as needed. Generate a corrected SQL query only.
"""

SUMMARIZE_RESULTS_PROMPT = """The user asked: "{question}"

Here are the query results (raw rows):

{results}

Summarize these results in one or two clear sentences in plain language for the user. Do not invent numbers or add information not present in the results."""
