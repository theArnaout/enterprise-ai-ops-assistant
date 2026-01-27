# Ticket Dataset Overview

## Source
This dataset is derived from a public IT service desk ticket dataset. A focused subset was created for analytical purposes.

## Dataset Scope
- Records represent internal operational tickets requiring review and resolution
- Dataset contains 502 records
- Data was filtered to English-language entries
- Only fields relevant to operational analysis were retained

## Fields

| Column Name  | Description                                                   |
|--------------|---------------------------------------------------------------|
| ticket_id    | Surrogate unique identifier added for analysis                |
| ticket_type  | Classification of the ticket (e.g. Request, Incident, Change) |
| priority     | Urgency level assigned to the ticket                          |
| category     | Functional category or routing group                          |
| assigned_to  | Team or function responsible for handling the ticket          |
| description  | Free-text description of the issue                            |

## Notes
- The source dataset did not include a unique identifier; a surrogate key was added
- Lifecycle status (e.g. Open, Closed) is not explicitly available in the source data
- Some fields were adapted to represent internal ownership and routing for analysis

