# Engineering Challenges & Learnings

This document captures notable technical challenges encountered during the project and how they were resolved. The intent is to document engineering decisions and lessons learned for future reference.

---

## 1. CSV Ingestion Limitations in Athena

**Challenge:**  
The source CSV contained malformed multi-line text fields that caused row misalignment and parsing errors in Amazon Athena.

**Resolution:**  
Introduced a preprocessing step using Python (pandas) and normalized the dataset into Apache Parquet prior to analysis.

**Learning:**  
CSV is not a reliable analytics format for complex text data in Athena. Converting to Parquet early improves correctness and performance.

---

## 2. S3 Prefix Hygiene for External Tables

**Challenge:**  
Athena returned misleading errors when table locations pointed to mixed-format files under the same S3 prefix.

**Resolution:**  
Separated raw CSV and Parquet outputs into distinct S3 prefixes and aligned Athena table locations accordingly.

**Learning:**  
Athena assumes all files under a table LOCATION share the same format.

---

## 3. Tooling & Environment Consistency

**Challenge:**  
Initial issues arose from mismatched Python environments and missing dependencies during local preprocessing.

**Resolution:**  
Standardized the environment and validated outputs locally before uploading to S3.

**Learning:**  
Early validation outside of cloud tools reduces debugging time and prevents misleading cloud errors.

