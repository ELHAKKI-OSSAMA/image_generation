# Database Schema: Image Generation Platform

## Core Structure
```
┌─────────────────┐
│  organizations  │──┐
└─────────────────┘  │
         │          ┌┴────────────┐
         │          │    users    │
         │          └─────────────┘
         │               │
    ┌────┼───────────┬──┴───┐
    │    │           │      │
┌───▼─┐ ┌▼──┐   ┌───▼──┐  ┌▼────────┐
│event│ │api │   │images│  │audit_log│
└─────┘ │keys│   └──────┘  └─────────┘
        └────┘      │          │
          │         │          │
    ┌─────┴─────────┴──────────┘
    │
┌───▼──────────────┐
│ usage_statistics │
└──────────────────┘
```

## Table Details

### organizations
```python
{
    "id": "uuid (pk)",
    "name": "varchar(255)",
    "status": ["pending", "active", "suspended"],
    "subscription_tier": ["trial", "basic", "premium", "enterprise"],
    "max_users": "integer",
    "max_storage_gb": "integer",
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

### users
```python
{
    "id": "uuid (pk)",
    "organization_id": "uuid (fk)",
    "email": "varchar(255) unique",
    "password_hash": "varchar(255)",
    "first_name": "varchar(100)",
    "last_name": "varchar(100)",
    "role": ["admin", "user"],
    "status": ["active", "inactive", "suspended"],
    "last_login": "timestamp"
}
```

### events
```python
{
    "id": "uuid (pk)",
    "organization_id": "uuid (fk)",
    "created_by": "uuid (fk → users)",
    "name": "varchar(255)",
    "description": "text",
    "start_date": "timestamp",
    "end_date": "timestamp",
    "status": ["upcoming", "ongoing", "completed", "cancelled"],
    "max_participants": "integer",
    "location": "varchar(255)"
}
```

### images
```python
{
    "id": "uuid (pk)",
    "event_id": "uuid (fk)",
    "organization_id": "uuid (fk)",
    "created_by": "uuid (fk → users)",
    "original_url": "text",
    "generated_url": "text",
    "prompt": "text",
    "status": ["processing", "completed", "failed"],
    "metadata": "jsonb",
    "processing_time": "integer (ms)"
}
```

### api_keys
```python
{
    "id": "uuid (pk)",
    "organization_id": "uuid (fk)",
    "created_by": "uuid (fk → users)",
    "key_hash": "varchar(255)",
    "name": "varchar(100)",
    "expires_at": "timestamp",
    "last_used_at": "timestamp",
    "status": ["active", "revoked"]
}
```

### usage_statistics
```python
{
    "id": "uuid (pk)",
    "organization_id": "uuid (fk)",
    "event_id": "uuid (fk)",
    "date": "date",
    "images_generated": "integer",
    "storage_used_bytes": "bigint",
    "api_calls": "integer"
}
```

### audit_logs
```python
{
    "id": "uuid (pk)",
    "organization_id": "uuid (fk)",
    "user_id": "uuid (fk)",
    "action": "varchar(100)",
    "resource_type": "varchar(50)",
    "resource_id": "uuid",
    "details": "jsonb",
    "ip_address": "inet",
    "user_agent": "text"
}
```

## Key Features

### Cascade Rules
- organization deletion → cascades to all related records
- event deletion → cascades to images and usage_statistics

### Performance Indexes
```sql
-- High-traffic queries
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_events_org ON events(organization_id);
CREATE INDEX idx_images_event ON images(event_id);
CREATE INDEX idx_usage_org_date ON usage_statistics(organization_id, date);
```

### Data Flow
```
1. Organization Setup
   organization → users → api_keys

2. Event Operations
   event → images → usage_statistics

3. Monitoring
   All operations → audit_logs
```
