# Engineering Challenges & Learnings

This document summarizes the main technical challenges I ran into during the project, how I approached them, and what I learned along the way.

The goal is not to present everything as perfect, but to document the actual problem-solving process.

---

## 1. CSV vs Parquet Ingestion in Athena

**Challenge:**  
Querying the raw CSV directly in Athena produced incorrect results. The initial row count was wrong, and even after cleaning the CSV so that it could be queried successfully, some results were still inconsistent and certain fields appeared misaligned.

This showed that the CSV format was fragile when dealing with complex text, quoting, and multiline values.

**What I tried:**  
- Attempted to clean multiline text fields in Python and re-export the CSV  
- Tested the cleaned CSV in Athena  
- Compared query results between CSV and Parquet versions  

**Resolution:**  
While the cleaned CSV could be queried, Parquet consistently produced correct and stable results across all validation queries. Because of this, Parquet was chosen as the final format for analysis.

**Learning:**  
CSV can appear to work but still introduce subtle data integrity issues. For analytics workflows, Parquet provides stronger guarantees and is more reliable.

---

## 2. S3 Prefix Hygiene for External Tables

**Challenge:**  
Athena produced confusing errors when different file formats (CSV and Parquet) were stored under the same S3 prefix for a table.

**Resolution:**  
I separated raw files and processed outputs into different S3 prefixes and ensured each Athena table only pointed to one format.

**Learning:**  
Athena assumes all files under a table LOCATION follow the same format, so keeping S3 folders clean is important.

---

## 3. Tooling & Environment Consistency

**Challenge:**  
Some issues early on were caused by mismatched Python environments and missing dependencies during local preprocessing.

**Resolution:**  
I standardized my virtual environment and validated outputs locally before uploading anything to S3.

**Learning:**  
Catching issues locally (before involving AWS services) saves a lot of debugging time.
