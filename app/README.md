# Streamlit demo

A simple web UI to try the AI Ops Assistant: chat with the agent and view a couple of charts from the ticket data.

## What it does

- **Chat tab:** Ask questions in plain English. The agent turns them into SQL, runs them on Athena, and returns a short summary. You can turn on "Show SQL in chat" in the sidebar to see the executed SQL. Follow-up questions work (e.g. "Break that down by category?").
- **Charts tab:** Bar charts come from **predefined Athena queries** in `agent/config.py` (same SQL templates the agent can use). You choose which charts to show via the multiselect: "Tickets by priority", "Tickets by owner", or "High priority by category". Only the charts you select are run and displayed.

## What you need

Same as the agent: Python 3.x, AWS credentials, `OPENAI_API_KEY`, and an Athena database/table pointing at your ticket data in S3. See [docs/08_how_to_run_agent.md](../docs/08_how_to_run_agent.md) for setup.

## How to run

From the **project root**:

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
# Optional: ATHENA_DATABASE, ATHENA_OUTPUT, etc.
streamlit run app/streamlit_app.py
```

Your browser will open to the app. Use the Chat tab to ask questions and the Charts tab to see the overview.

## Clear chat

Use the "Clear chat" button in the Chat tab to reset the conversation (and follow-up context).
