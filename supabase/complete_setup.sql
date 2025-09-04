-- Open Horizon AI - Complete Supabase Setup
-- Run this script in your Supabase SQL Editor to set up the database

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE project_status AS ENUM (
        'brainstorming', 
        'planning', 
        'partnering', 
        'writing', 
        'review', 
        'submitted', 
        'approved', 
        'active'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE organization_type AS ENUM (
        'NGO', 
        'Public Body', 
        'School', 
        'Higher Education Institution', 
        'Company', 
        'Other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Settings table for application configuration
CREATE TABLE IF NOT EXISTS open_horizon_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_name TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    focus_area TEXT NOT NULL,
    target_audience TEXT,
    innovation_angle TEXT,
    status project_status DEFAULT 'brainstorming',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),
    
    -- Erasmus+ specific fields
    duration_months INTEGER CHECK (duration_months >= 3 AND duration_months <= 36),
    budget_estimate_eur DECIMAL(10,2) CHECK (budget_estimate_eur >= 0),
    countries_involved TEXT[],
    
    -- JSON fields for flexible data
    brainstorm_concepts JSONB DEFAULT '[]'::jsonb,
    partner_search_results JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Partners table  
CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    organization_type organization_type,
    expertise_areas TEXT[],
    erasmus_code TEXT UNIQUE,
    contact_email TEXT,
    contact_website TEXT,
    contact_phone TEXT,
    compatibility_score INTEGER CHECK (compatibility_score >= 1 AND compatibility_score <= 10),
    partnership_rationale TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb
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

-- Partner Searches table (for caching and analytics)
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

-- User Sessions table (for CLI and API session management)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Erasmus+ Knowledge Base (similar to Archon's crawled_pages)
CREATE TABLE IF NOT EXISTS erasmus_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_url TEXT,
    source_type TEXT, -- 'programme_guide', 'national_agency', 'best_practice'
    section TEXT, -- Section of Programme Guide or document type
    embedding vector(1536), -- OpenAI embedding dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_focus_area ON projects(focus_area);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);

CREATE INDEX IF NOT EXISTS idx_partners_country ON partners(country);
CREATE INDEX IF NOT EXISTS idx_partners_organization_type ON partners(organization_type);
CREATE INDEX IF NOT EXISTS idx_partners_expertise_areas ON partners USING GIN(expertise_areas);
CREATE INDEX IF NOT EXISTS idx_partners_erasmus_code ON partners(erasmus_code);

CREATE INDEX IF NOT EXISTS idx_application_sections_project_id ON application_sections(project_id);
CREATE INDEX IF NOT EXISTS idx_application_sections_section_name ON application_sections(section_name);
CREATE INDEX IF NOT EXISTS idx_application_sections_user_id ON application_sections(user_id);

CREATE INDEX IF NOT EXISTS idx_partner_searches_project_id ON partner_searches(project_id);
CREATE INDEX IF NOT EXISTS idx_partner_searches_user_id ON partner_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_partner_searches_searched_at ON partner_searches(searched_at);

CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_active ON user_sessions(last_active);

-- Vector similarity search index
CREATE INDEX IF NOT EXISTS idx_erasmus_knowledge_embedding ON erasmus_knowledge USING ivfflat (embedding vector_cosine_ops);

-- Functions for vector similarity search (similar to Archon)
CREATE OR REPLACE FUNCTION match_erasmus_knowledge(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.78,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    title text,
    content text,
    source_url text,
    source_type text,
    section text,
    similarity float,
    metadata jsonb
)
LANGUAGE sql STABLE
AS $$
    SELECT
        ek.id,
        ek.title,
        ek.content,
        ek.source_url,
        ek.source_type,
        ek.section,
        1 - (ek.embedding <=> query_embedding) AS similarity,
        ek.metadata
    FROM erasmus_knowledge ek
    WHERE 1 - (ek.embedding <=> query_embedding) > match_threshold
    ORDER BY ek.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for auto-updating timestamps
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_partners_updated_at BEFORE UPDATE ON partners FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_application_sections_updated_at BEFORE UPDATE ON application_sections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_erasmus_knowledge_updated_at BEFORE UPDATE ON erasmus_knowledge FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_open_horizon_settings_updated_at BEFORE UPDATE ON open_horizon_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE application_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE partner_searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Projects policies
CREATE POLICY "Users can view their own projects" ON projects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own projects" ON projects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own projects" ON projects
    FOR DELETE USING (auth.uid() = user_id);

-- Application sections policies
CREATE POLICY "Users can view their own application sections" ON application_sections
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own application sections" ON application_sections
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own application sections" ON application_sections
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own application sections" ON application_sections
    FOR DELETE USING (auth.uid() = user_id);

-- Partner searches policies
CREATE POLICY "Users can view their own partner searches" ON partner_searches
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own partner searches" ON partner_searches
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User sessions policies
CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own sessions" ON user_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own sessions" ON user_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- Partners table is public (read-only for all authenticated users)
CREATE POLICY "Authenticated users can view partners" ON partners
    FOR SELECT TO authenticated USING (true);

-- Erasmus knowledge is public (read-only for all authenticated users)
CREATE POLICY "Authenticated users can view erasmus knowledge" ON erasmus_knowledge
    FOR SELECT TO authenticated USING (true);

-- Insert sample data for development
INSERT INTO open_horizon_settings (setting_name, setting_value, description) VALUES
    ('app_version', '1.0.0', 'Application version'),
    ('default_language', 'en', 'Default language for the application'),
    ('organization_name', 'Open Horizon', 'Default organization name'),
    ('organization_country', 'Sweden', 'Default organization country'),
    ('erasmus_program_year', '2024', 'Current Erasmus+ programme year')
ON CONFLICT (setting_name) DO NOTHING;

INSERT INTO partners (name, country, organization_type, expertise_areas, erasmus_code, contact_email, contact_website, compatibility_score, partnership_rationale, verified) 
VALUES 
    ('Digital Youth Foundation', 'Germany', 'NGO', ARRAY['Digital Skills', 'Youth Work', 'Innovation'], 'DE-YOUTH-001', 'contact@digitalyouth.de', 'https://digitalyouth.de', 9, 'Strong digital expertise and proven track record in youth projects', TRUE),
    ('Green Action Network', 'Netherlands', 'NGO', ARRAY['Environmental Education', 'Sustainability', 'Community Engagement'], 'NL-GREEN-002', 'info@greenaction.nl', 'https://greenaction.nl', 8, 'Excellent environmental focus with European-wide networks', TRUE),
    ('Inclusion Works', 'Spain', 'Public Body', ARRAY['Social Inclusion', 'Diversity Training', 'Youth Support'], 'ES-INCL-003', 'hello@inclusionworks.es', 'https://inclusionworks.es', 7, 'Specialized in inclusion work with vulnerable groups', TRUE),
    ('Innovation Academy', 'Finland', 'Higher Education Institution', ARRAY['Innovation', 'Entrepreneurship', 'Technology'], 'FI-INNOV-004', 'partnerships@innovacademy.fi', 'https://innovacademy.fi', 8, 'Academic excellence in innovation and strong research capabilities', TRUE),
    ('Youth Bridge Europe', 'France', 'NGO', ARRAY['Cultural Exchange', 'Language Learning', 'European Citizenship'], 'FR-BRIDGE-005', 'europe@youthbridge.fr', 'https://youthbridge.fr', 7, 'Extensive experience in cross-cultural youth programs', TRUE),
    ('Tech for Good Initiative', 'Italy', 'Company', ARRAY['Digital Transformation', 'Social Innovation', 'Accessibility'], 'IT-TECH-006', 'partnerships@techforgood.it', 'https://techforgood.it', 6, 'Private sector expertise in technology for social impact', TRUE),
    ('Nordic Youth Collective', 'Norway', 'NGO', ARRAY['Youth Participation', 'Democratic Values', 'Nordic Cooperation'], 'NO-NORDIC-007', 'contact@nordicyouth.no', 'https://nordicyouth.no', 8, 'Strong Nordic perspective and democratic participation focus', TRUE),
    ('Baltic Innovation Hub', 'Estonia', 'Public Body', ARRAY['Digital Innovation', 'Startups', 'E-governance'], 'EE-BALTIC-008', 'partnerships@baltichub.ee', 'https://baltichub.ee', 7, 'Digital innovation expertise from one of Europe\'s most digital societies', TRUE)
ON CONFLICT (erasmus_code) DO NOTHING;

-- Insert sample Erasmus+ knowledge content
INSERT INTO erasmus_knowledge (title, content, source_type, section, metadata) VALUES
    ('Erasmus+ Programme Priorities 2024-2025', 'The Erasmus+ programme focuses on four key priorities: Inclusion and diversity, Digital transformation, Environment and fight against climate change, and Participation in democratic life and common values. These priorities should be reflected in all project applications to ensure alignment with EU objectives.', 'programme_guide', 'Programme Priorities', '{"year": "2024", "importance": "critical"}'),
    ('Swedish National Agency MUCF Guidelines', 'MUCF (Myndigheten för ungdoms- och civilsamhällesfrågor) handles Youth and Sport applications in Sweden. Applications must be submitted through the MUCF portal with specific attention to Swedish national priorities including democratic participation, sustainability, and inclusion of marginalized youth.', 'national_agency', 'Sweden MUCF', '{"agency": "MUCF", "country": "Sweden", "sectors": ["youth", "sport"]}'),
    ('Partner Eligibility Criteria', 'Eligible partner organizations must be legally established in Programme Countries or Partner Countries. They must have the operational capacity to implement project activities and contribute to project objectives. Public bodies, NGOs, educational institutions, and private organizations can all be partners under specific conditions.', 'programme_guide', 'Partner Eligibility', '{"critical": true, "applies_to": "all_actions"}'),
    ('Budget and Funding Rules', 'Erasmus+ projects are funded through unit costs and lump sums. Travel costs are calculated based on distance bands, organizational support uses per-participant rates, and special needs support is available for inclusion measures. Green travel receives additional top-up funding.', 'programme_guide', 'Budget Rules', '{"funding_type": "unit_costs", "green_travel": true}')
ON CONFLICT DO NOTHING;

-- Function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_sessions INTEGER;
    deleted_searches INTEGER;
BEGIN
    -- Clean up old sessions (older than 30 days)
    DELETE FROM user_sessions 
    WHERE last_active < NOW() - INTERVAL '30 days';
    GET DIAGNOSTICS deleted_sessions = ROW_COUNT;
    
    -- Clean up old partner searches (older than 90 days)
    DELETE FROM partner_searches 
    WHERE searched_at < NOW() - INTERVAL '90 days';
    GET DIAGNOSTICS deleted_searches = ROW_COUNT;
    
    RETURN deleted_sessions + deleted_searches;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON DATABASE current_database() IS 'Open Horizon AI - Erasmus+ Project Management System Database';
COMMENT ON TABLE projects IS 'Erasmus+ project information with status tracking and EU compliance';
COMMENT ON TABLE partners IS 'European partner organizations database for Erasmus+ projects';
COMMENT ON TABLE application_sections IS 'Generated application content with compliance checking';
COMMENT ON TABLE partner_searches IS 'Search history and caching for partner discovery';
COMMENT ON TABLE user_sessions IS 'Session management for CLI and API users';
COMMENT ON TABLE erasmus_knowledge IS 'Erasmus+ Programme Guide and knowledge base for RAG';
COMMENT ON FUNCTION match_erasmus_knowledge IS 'Vector similarity search for Erasmus+ knowledge';
COMMENT ON FUNCTION cleanup_old_data IS 'Maintenance function to clean up old sessions and searches';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Open Horizon AI database setup completed successfully!';
    RAISE NOTICE 'Created tables: projects, partners, application_sections, partner_searches, user_sessions, erasmus_knowledge';
    RAISE NOTICE 'Configured RLS policies for data security';
    RAISE NOTICE 'Inserted sample data for development';
    RAISE NOTICE 'Vector search enabled for knowledge base';
END $$;