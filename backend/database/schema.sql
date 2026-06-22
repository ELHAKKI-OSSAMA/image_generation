-- PostgreSQL Database Schema for Image Generation Web Application
-- Description: B2B platform for AI-powered image generation events
-- Author: Ofotolab

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom enum types
CREATE TYPE userrole AS ENUM ('user', 'admin', 'super_admin', 'organization', 'member');
CREATE TYPE verificationstatus AS ENUM ('pending', 'verified', 'rejected');
CREATE TYPE organizationstatus AS ENUM ('pending', 'active', 'inactive', 'suspended');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role userrole NOT NULL,
    permissions JSONB NOT NULL DEFAULT '{}',
    status verificationstatus NOT NULL DEFAULT 'pending',
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_token_expires_at TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Admins table (platform administrators)
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_admin_status CHECK (status IN ('active', 'inactive'))
);

-- Organizations table (B2B clients)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    status organizationstatus NOT NULL DEFAULT 'pending',
    approved_by UUID REFERENCES admins(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    subscription_tier VARCHAR(50) DEFAULT 'trial',
    max_users INTEGER DEFAULT 5,
    max_storage_gb INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_org_status CHECK (status IN ('pending', 'active', 'inactive', 'suspended')),
    CONSTRAINT chk_subscription CHECK (subscription_tier IN ('trial', 'basic', 'premium', 'enterprise'))
);

-- Organization Members table
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_member_role CHECK (role IN ('owner', 'manager', 'member')),
    CONSTRAINT chk_member_status CHECK (status IN ('active', 'inactive', 'suspended')),
    UNIQUE(organization_id, email)
);

-- Events table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'upcoming',
    created_by UUID NOT NULL REFERENCES organization_members(id),
    max_participants INTEGER,
    location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_event_status CHECK (status IN ('upcoming', 'ongoing', 'completed', 'cancelled'))
);

-- Event Participants table
CREATE TABLE event_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    participant_name VARCHAR(255) NOT NULL,
    participant_email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Images table
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    participant_id UUID NOT NULL REFERENCES event_participants(id),
    original_url TEXT NOT NULL,
    generated_url TEXT,
    prompt TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'processing',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    processing_time INTEGER, -- in milliseconds
    CONSTRAINT chk_image_status CHECK (status IN ('processing', 'completed', 'failed'))
);

-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_by UUID NOT NULL REFERENCES organization_members(id),
    approved_by UUID NOT NULL REFERENCES admins(id),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    CONSTRAINT chk_apikey_status CHECK (status IN ('active', 'revoked'))
);

-- Usage Statistics table
CREATE TABLE usage_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    images_generated INTEGER DEFAULT 0,
    storage_used_bytes BIGINT DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id),
    admin_id UUID REFERENCES admins(id),
    member_id UUID REFERENCES organization_members(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_org_members_organization ON organization_members(organization_id);
CREATE INDEX idx_events_organization ON events(organization_id);
CREATE INDEX idx_images_event ON images(event_id);
CREATE INDEX idx_images_participant ON images(participant_id);
CREATE INDEX idx_participants_event ON event_participants(event_id);
CREATE INDEX idx_usage_stats_organization ON usage_statistics(organization_id);
CREATE INDEX idx_audit_logs_organization ON audit_logs(organization_id);
CREATE INDEX idx_audit_logs_admin ON audit_logs(admin_id);
CREATE INDEX idx_audit_logs_member ON audit_logs(member_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updating updated_at
CREATE TRIGGER update_organization_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_org_member_updated_at
    BEFORE UPDATE ON organization_members
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_event_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_image_updated_at
    BEFORE UPDATE ON images
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
