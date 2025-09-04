-- Open Horizon AI - Simple Supabase Setup
-- Run this script in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    focus_area TEXT NOT NULL,
    target_audience TEXT,
    innovation_angle TEXT,
    status TEXT DEFAULT 'brainstorming',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),
    
    -- Erasmus+ specific fields
    duration_months INTEGER,
    budget_estimate_eur DECIMAL(10,2),
    countries_involved TEXT[],
    
    -- JSON fields for flexible data
    brainstorm_concepts JSONB DEFAULT '[]'::jsonb,
    partner_search_results JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Constraints
    CONSTRAINT projects_duration_check CHECK (duration_months IS NULL OR (duration_months >= 3 AND duration_months <= 36)),
    CONSTRAINT projects_budget_check CHECK (budget_estimate_eur IS NULL OR budget_estimate_eur >= 0)
);

-- Partners table  
CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    organization_type TEXT,
    expertise_areas TEXT[],
    erasmus_code TEXT UNIQUE,
    contact_email TEXT,
    contact_website TEXT,
    contact_phone TEXT,
    compatibility_score INTEGER,
    partnership_rationale TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Constraints
    CONSTRAINT partners_score_check CHECK (compatibility_score IS NULL OR (compatibility_score >= 1 AND compatibility_score <= 10))
);

-- Project Partners junction table
CREATE TABLE IF NOT EXISTS project_partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    partner_id UUID REFERENCES partners(id) ON DELETE CASCADE,
    role TEXT,
    status TEXT DEFAULT 'potential',
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(project_id, partner_id)
);

-- Application Sections table
CREATE TABLE IF NOT EXISTS application_sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    section_name TEXT NOT NULL,
    content TEXT,
    word_count INTEGER DEFAULT 0,
    compliance_status BOOLEAN DEFAULT FALSE,
    suggestions TEXT[],
    compliance_details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    user_id UUID REFERENCES auth.users(id)
);

-- Partner Searches table
CREATE TABLE IF NOT EXISTS partner_searches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    search_query TEXT NOT NULL,
    required_countries TEXT[],
    expertise_areas TEXT[],
    partners_found JSONB DEFAULT '[]'::jsonb,
    searched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- User Sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Settings table
CREATE TABLE IF NOT EXISTS open_horizon_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_name TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);