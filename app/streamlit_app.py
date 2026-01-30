"""
Streamlit demo: chat with the agent and view simple charts from ticket data.
Run from project root: streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

# Ensure project root is on path so "agent" package resolves
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd

from agent.agent import ask_agent
from agent.config import CONVERSATION_HISTORY_SIZE, SQL_TEMPLATES
from agent.tools import run_athena_query


def athena_rows_to_dataframe(rows: list) -> pd.DataFrame:
    """Turn Athena result rows (first row = header) into a pandas DataFrame."""
    if not rows:
        return pd.DataFrame()
    header = rows[0]
    col_names = [(c or {}).get("VarCharValue", "") for c in (header.get("Data") or [])]
    data = []
    for row in rows[1:]:
        data.append([(c or {}).get("VarCharValue", "") for c in (row.get("Data") or [])])
    return pd.DataFrame(data, columns=col_names)


# Chart options: label shown in UI -> key in agent.config.SQL_TEMPLATES
CHART_OPTIONS = [
    ("Tickets by priority", "tickets_by_priority"),
    ("Tickets by category", "tickets_by_category"),
    ("High priority by category", "high_priority_by_category"),
    ("Tickets by owner", "tickets_by_owner"),
]


def fetch_total_tickets() -> int | None:
    """Run total_tickets query and return the count, or None on error."""
    if "total_tickets" not in SQL_TEMPLATES:
        return None
    try:
        rows = run_athena_query(SQL_TEMPLATES["total_tickets"])
        df = athena_rows_to_dataframe(rows)
        if df is not None and not df.empty and "total_tickets" in df.columns:
            return int(pd.to_numeric(df["total_tickets"].iloc[0], errors="coerce"))
        return None
    except Exception:
        return None


def fetch_chart_data(template_key: str) -> pd.DataFrame | None:
    """Run one predefined Athena query and return a DataFrame for that chart, or None on error."""
    if template_key not in SQL_TEMPLATES:
        return None
    try:
        rows = run_athena_query(SQL_TEMPLATES[template_key])
        return athena_rows_to_dataframe(rows)
    except Exception:
        return None


st.set_page_config(
    page_title="AI Ops Assistant",
    page_icon="📊",
    layout="wide",
)

st.title("AI Ops Assistant")
st.caption("Ask questions about support ticket data in plain English. Results come from Athena (S3).")

# Sidebar
with st.sidebar:
    st.header("Options")
    show_sql = st.checkbox("Show SQL in chat", value=False, help="Print the executed SQL after each answer so you can verify in Athena.")
    st.divider()
    st.markdown("**How to run (CLI)**")
    st.code("python -m agent.run", language="bash")
    st.markdown("See [docs/08_how_to_run_agent.md](../docs/08_how_to_run_agent.md) for setup.")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

tab_chat, tab_charts = st.tabs(["Chat", "Charts"])

# --- Chat tab ---
with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sql") and show_sql:
                with st.expander("SQL run (for verification)"):
                    st.code(msg["sql"], language="sql")

    if prompt := st.chat_input("Ask a question about the ticket data…"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                history = st.session_state.conversation_history[-CONVERSATION_HISTORY_SIZE:] if st.session_state.conversation_history else None
                result = ask_agent(
                    prompt,
                    return_sql=show_sql,
                    conversation_history=history,
                )
                if isinstance(result, dict):
                    summary = result["summary"]
                    sql_used = result.get("sql")
                else:
                    summary = result
                    sql_used = None
                st.markdown(summary)
                if show_sql and sql_used:
                    with st.expander("SQL run (for verification)"):
                        st.code(sql_used, language="sql")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": summary,
                    "sql": sql_used,
                })
                st.session_state.conversation_history.append((prompt, summary))
            except Exception as e:
                st.error(str(e))
                st.session_state.messages.append({"role": "assistant", "content": str(e), "sql": None})

    if st.button("Clear chat", type="secondary"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()

# --- Charts tab ---
with tab_charts:
    st.subheader("Ticket overview (from Athena)")
    st.caption("Charts come from predefined Athena queries. Choose which ones to run and display below.")

    # Header metric: total tickets
    total = fetch_total_tickets()
    if total is not None:
        st.metric("Total tickets", f"{total:,}")
    else:
        st.caption("Total tickets — could not load (check Athena and AWS setup).")

    selected = st.multiselect(
        "Which charts to show",
        options=[key for _, key in CHART_OPTIONS],
        default=["tickets_by_priority", "tickets_by_category", "high_priority_by_category", "tickets_by_owner"],
        format_func=lambda k: next(label for label, key in CHART_OPTIONS if key == k),
    )
    if not selected:
        st.info("Select at least one chart above.")
    else:
        any_ok = False
        for template_key in selected:
            df = fetch_chart_data(template_key)
            label = next(label for label, key in CHART_OPTIONS if key == template_key)
            if df is not None and not df.empty:
                any_ok = True
                cols = df.columns.tolist()
                count_col = cols[1] if len(cols) > 1 else "ticket_count"
                df[count_col] = pd.to_numeric(df[count_col], errors="coerce").fillna(0)
                st.markdown(f"**{label}**")
                # Top N selector for tickets_by_category only
                if template_key == "tickets_by_category":
                    top_n = st.number_input(
                        "Top N categories",
                        min_value=1,
                        max_value=min(50, len(df)),
                        value=min(10, len(df)),
                        key="top_n_category",
                    )
                    df = df.head(top_n)
                st.bar_chart(df.set_index(cols[0]))
            else:
                st.warning(f"**{label}** — could not load data (check Athena and AWS setup).")
        if not any_ok:
            st.info("Charts need Athena and the ticket table to be set up. Set AWS credentials and ATHENA_* env vars, then run a query in the Chat tab first to confirm the connection.")
