# Orders Service

Handles ~500 req/s. PostgreSQL 15 single instance (no read replicas yet).

## Current pain points
- `orders` table is denormalized: one row per line-item
- Reporting queries do expensive self-joins to group by order
- Adding a new item to an existing order requires UPDATE across N rows
- No soft-delete; hard deletes lose audit trail

## Constraints
- Cannot take the service offline (SLA: 99.95%)
- No data loss tolerated
- Team of 2 DBAs available during migration window
- Change freeze: first 2 weeks of the month
