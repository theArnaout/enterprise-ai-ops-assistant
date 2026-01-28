# SQL Queries

This folder contains the SQL queries used to explore, profile, and analyze the support ticket dataset using Amazon Athena.

The queries are organized by purpose and follow a progressive workflow:
1. Validate and understand the dataset
2. Derive basic operational metrics
3. Support downstream reporting and AI-assisted analysis

---

## File Overview

### `01_data_profiling.sql`
Queries focused on:
- Validating row counts after ingestion
- Understanding distributions (priority, category, type)
- Identifying potential data quality issues (e.g., missing assignments)

These queries were run first to ensure the dataset is suitable for analysis.

---

### `02_operational_metrics.sql`
Queries focused on:
- Identifying high-impact operational areas
- Highlighting high-priority ticket concentrations
- Supporting business-facing insights and reporting

These queries are used as inputs for documentation, dashboards, and AI-assisted summaries.

---

## Execution Environment

All queries are designed to run in **Amazon Athena** against the `ops_data.tickets` external table backed by Parquet files stored in Amazon S3.

The SQL is ANSI-compliant where possible and intentionally kept simple for clarity and maintainability.

