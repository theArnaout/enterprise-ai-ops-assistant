# \## Power BI – Support Ticket Analytics Dashboard

# 

# This dashboard provides a reviewer-friendly view of operational support ticket data.

# It is designed as a \*\*read-only analytics layer\*\* backed by SQL validation in Amazon Athena.

# 

# \### What this dashboard shows

# \- Total ticket volume and severity distribution

# \- Concentration of high-priority tickets by category

# \- Workload distribution across support teams

# 

# \### Design choices

# \- KPI cards are used for top-level operational signals

# \- Bar charts are used for category and team comparisons to support accurate ranking

# \- Donut charts are used for small, fixed distributions (ticket priority)

# 

# \### Data \& validation

# \- Source data is stored in Amazon S3 and queried via Amazon Athena

# \- Dashboard metrics are validated against SQL queries

# \- Power BI is used strictly for visualization and review

# 

# \### Limitations

# \- The dataset does not include timestamps or SLA clocks

# \- Time-based metrics (resolution time, SLA breaches, backlog aging) are out of scope

# \- These metrics would be added in a production support environment

# 

# \### Relationship to AI Assistant

# This dashboard complements the AI-assisted analytics agent in the project:

# \- Power BI shows \*what\* is happening

# \- Athena validates \*why\*

# \- The AI assistant explains patterns and drafts summaries for human review

