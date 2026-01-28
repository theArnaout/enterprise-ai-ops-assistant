-- High priority tickets by category
SELECT
  category,
  COUNT(*) AS high_priority_tickets
FROM ops_data.tickets
WHERE priority = 'high'
GROUP BY category
ORDER BY high_priority_tickets DESC;

-- Ticket volume by type (incident, request, change, etc.)
SELECT
  ticket_type,
  COUNT(*) AS ticket_count
FROM ops_data.tickets
GROUP BY ticket_type
ORDER BY ticket_count DESC;
