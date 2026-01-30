# Delivery Plan

## Delivery Approach
This project follows a hybrid Agile approach. The overall scope and architecture are defined upfront, while features are delivered in small, focused iterations.

## Project Phases
- Phase 0: Discovery and Design
- Phase 1: Data Foundation
- Phase 2: Analytics and Visualization
- Phase 3: AI Assistant Prototype
- Phase 4: Enablement and Review

## Working Style
- Short, goal-oriented phases
- Documentation created alongside implementation
- Demo-ready artifacts at the end of each phase

## Current phase
- **Phase 4 (Enablement and Review)** — Phase 3 (AI Assistant Prototype) is done: LLM-generated SQL, Athena execution, guardrails, retries, schema enrichment, and conversation context are implemented. A **Streamlit demo** (`app/streamlit_app.py`) provides a chat UI and simple charts for demos. Documentation and enablement materials (READMEs, how-to guide, agent design) are in place.

## Next steps
- Phase 4: finalize enablement (FAQs, internal demos using the Streamlit app).
- Optional: audit log (question + SQL + timestamp); Phase 3b (e.g. LangChain agent with tools).

## Documentation and enablement
Documentation and enablement are explicit deliverables: root and agent READMEs, [app/README.md](../app/README.md) (Streamlit demo), [docs/08_how_to_run_agent.md](08_how_to_run_agent.md) (step-by-step and FAQs), [docs/07_agent_design.md](07_agent_design.md) (design and current implementation). The Streamlit app gives a demo-ready UI (chat + charts) for internal demos. These support the role’s focus on how-to guides, job aids, and internal enablement.

