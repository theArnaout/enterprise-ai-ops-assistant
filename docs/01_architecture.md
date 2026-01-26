# Architecture Overview

## High-Level Architecture

        Data Source
            |
            V
          AWS S3
            |
            V
         AWS Athena 
       (SQL Queries)
            |
            V
     Power BI Dashboard
         Assistant
            |
            V
    Human Review & Action
    

## Component Description

- **Data Source:** A structured dataset representing internal operational records
- **AWS S3:** Central storage for raw and processed data
- **AWS Athena:** Serverless SQL engine used for data exploration and validation
- **Power BI:** Visualization layer for trends and exceptions
- **AI Ops Assistant:** Prompt-driven assistant that explains data and drafts summaries
- **Human Review:** Users review, edit, and decide on all outcomes

## Design Principles
- Human-in-the-loop by default
- Decision support, not decision replacement
- Clear separation between data, analysis, and presentation
- Simple, explainable system behavior

