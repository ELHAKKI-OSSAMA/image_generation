# Image Generation B2B Database Schema

## Core Tables and Relationships

```
[Organizations] ═══════════════════════╗
     ║                                ║
     ║                                ║
     ▼                                ▼
  [Users] ══════════════▶ [Events] ═══════▶ [Images]
     ║           creates     ║               ▲
     ║                      ║               ║
     ▼                      ▼               ║
[API Keys]          [Usage Statistics] ══════╝
     ║                      ║
     ╚═════════▶ [Audit Logs] ◄════════════╝

Legend:
═══▶ One-to-Many relationship
────▶ Creates/Owns relationship
```

## Table Details

### 1️⃣ Core B2B Tables

#### 🏢 Organizations
```diff
+ Primary Table - Controls access and permissions
! id (UUID) PRIMARY KEY
+ name (varchar) - Organization name
+ status (varchar) - pending/active/suspended
# subscription_tier - trial/basic/premium/enterprise
- max_users (int) - User quota
- max_storage_gb (int) - Storage quota
```

#### 👥 Users
```diff
+ Linked to Organizations
! id (UUID) PRIMARY KEY
# organization_id (UUID) FOREIGN KEY
+ email (varchar) UNIQUE
- password_hash (varchar)
+ role - admin/user
+ status - active/inactive/suspended
```

### 2️⃣ Operational Tables

#### 📅 Events
```diff
+ Core business logic table
! id (UUID) PRIMARY KEY
# organization_id (UUID) FOREIGN KEY
# created_by (UUID) -> Users
+ name, description
+ start_date, end_date
+ status - upcoming/ongoing/completed/cancelled
- max_participants, location
```

#### 🖼️ Images
```diff
+ Main product data
! id (UUID) PRIMARY KEY
# event_id (UUID) FOREIGN KEY
# organization_id (UUID) FOREIGN KEY
# created_by (UUID) -> Users
+ original_url, generated_url
- prompt, metadata (jsonb)
+ status - processing/completed/failed
- processing_time (ms)
```

### 3️⃣ Security & Monitoring

#### 🔐 API Keys
```diff
+ API Access Control
! id (UUID) PRIMARY KEY
# organization_id (UUID) FOREIGN KEY
+ key_hash (varchar)
+ name (varchar)
- expires_at (timestamp)
+ status - active/revoked
```

#### 📊 Usage Statistics
```diff
+ Usage Tracking
! id (UUID) PRIMARY KEY
# organization_id (UUID) FOREIGN KEY
# event_id (UUID) FOREIGN KEY
+ date (date)
- images_generated (int)
- storage_used_bytes (bigint)
- api_calls (int)
```

#### 📝 Audit Logs
```diff
+ Security Audit Trail
! id (UUID) PRIMARY KEY
# organization_id (UUID) FOREIGN KEY
# user_id (UUID) FOREIGN KEY
+ action (varchar)
+ resource_type (varchar)
- resource_id (UUID)
- details (jsonb)
+ ip_address, user_agent
```

## Color Key
```diff
! Primary Keys (Yellow)
# Foreign Keys (Blue)
+ Required Fields (Green)
- Optional Fields (Gray)
```

## Cascade Rules

```
Organizations
├── ⚡ DELETE CASCADE
│   ├── Users
│   ├── Events
│   │   └── Images
│   ├── API Keys
│   ├── Usage Statistics
│   └── Audit Logs
```

## Performance Indexes

```
📈 High-Performance Queries
├── Organizations
│   └── (name, status)
├── Users
│   └── (organization_id, email)
├── Events
│   └── (organization_id, status, date)
├── Images
│   └── (event_id, status)
└── Audit Logs
    └── (organization_id, created_at)
```

## Data Flow Example

```
1. Organization Registration
   └── Create Organization
       └── Create Admin User
           └── Generate API Key
               └── Log in Audit

2. Event Creation
   └── Create Event
       └── Generate Images
           └── Update Usage Stats
               └── Log in Audit
```

This visualization uses:
- Clear hierarchical structure
- Color-coded elements
- ASCII art for relationships
- Consistent formatting
- Emoji for visual categorization
- Different section styles for different types of information
