-- Basic row count to validate dataset size
SELECT COUNT(*) AS total_tickets
FROM ops_data.tickets;

-- Distribution of ticket priority
SELECT
  priority,
  COUNT(*) AS ticket_count
FROM ops_data.tickets
GROUP BY priority
ORDER BY ticket_count DESC;

-- Distribution by category (queue)
SELECT
  category,
  COUNT(*) AS ticket_count
FROM ops_data.tickets
GROUP BY category
ORDER BY ticket_count DESC;

-- Check for unassigned tickets
SELECT
  COUNT(*) AS unassigned_tickets
FROM ops_data.tickets
WHERE assigned_to IS NULL OR assigned_to = '';
