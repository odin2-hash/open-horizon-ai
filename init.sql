-- Open Horizon AI Database Schema
-- PostgreSQL initialization script (optional - for local development)

-- Create database if using local postgres
-- This is automatically run if using the postgres service in docker-compose

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    focus_area TEXT NOT NULL,
    target_audience TEXT,
    innovation_angle TEXT,
    status TEXT DEFAULT 'brainstorming',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_id TEXT,
    
    -- Erasmus+ specific fields
    duration_months INTEGER CHECK (duration_months >= 3 AND duration_months <= 36),
    budget_estimate_eur DECIMAL(10,2) CHECK (budget_estimate_eur >= 0),
    countries_involved TEXT[],
    
    -- JSON fields for flexible data
    brainstorm_concepts JSONB,
    partner_search_results JSONB,
    metadata JSONB
);

-- Partners table  
CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    organization_type TEXT,
    expertise_areas TEXT[],
    erasmus_code TEXT UNIQUE,
    contact_email TEXT,
    contact_website TEXT,
    contact_phone TEXT,
    compatibility_score INTEGER CHECK (compatibility_score >= 1 AND compatibility_score <= 10),
    partnership_rationale TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

-- Project Partners junction table
CREATE TABLE IF NOT EXISTS project_partners (
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    partner_id UUID REFERENCES partners(id) ON DELETE CASCADE,
    role TEXT,
    status TEXT DEFAULT 'potential',
    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (project_id, partner_id)
);

-- Application Sections table
CREATE TABLE IF NOT EXISTS application_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    section_name TEXT NOT NULL,
    content TEXT,
    word_count INTEGER DEFAULT 0,
    compliance_status BOOLEAN DEFAULT FALSE,
    suggestions TEXT[],
    compliance_details JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Partner Searches table (for caching and analytics)
CREATE TABLE IF NOT EXISTS partner_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    search_query TEXT NOT NULL,
    required_countries TEXT[],
    expertise_areas TEXT[],
    partners_found JSONB,
    searched_at TIMESTAMP DEFAULT NOW(),
    user_id TEXT
);

-- User Sessions table (for CLI and API session management)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    metadata JSONB
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

CREATE INDEX IF NOT EXISTS idx_partner_searches_project_id ON partner_searches(project_id);
CREATE INDEX IF NOT EXISTS idx_partner_searches_searched_at ON partner_searches(searched_at);

CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_active ON user_sessions(last_active);

-- Insert sample data for development
INSERT INTO partners (name, country, organization_type, expertise_areas, erasmus_code, contact_email, contact_website, compatibility_score, partnership_rationale, verified) 
VALUES 
    ('Digital Youth Foundation', 'Germany', 'NGO', ARRAY['Digital Skills', 'Youth Work', 'Innovation'], 'DE-YOUTH-001', 'contact@digitalyouth.de', 'https://digitalyouth.de', 9, 'Strong digital expertise and proven track record in youth projects', TRUE),
    ('Green Action Network', 'Netherlands', 'NGO', ARRAY['Environmental Education', 'Sustainability', 'Community Engagement'], 'NL-GREEN-002', 'info@greenaction.nl', 'https://greenaction.nl', 8, 'Excellent environmental focus with European-wide networks', TRUE),
    ('Inclusion Works', 'Spain', 'Public Body', ARRAY['Social Inclusion', 'Diversity Training', 'Youth Support'], 'ES-INCL-003', 'hello@inclusionworks.es', 'https://inclusionworks.es', 7, 'Specialized in inclusion work with vulnerable groups', TRUE),
    ('Innovation Academy', 'Finland', 'Higher Education Institution', ARRAY['Innovation', 'Entrepreneurship', 'Technology'], 'FI-INNOV-004', 'partnerships@innovacademy.fi', 'https://innovacademy.fi', 8, 'Academic excellence in innovation and strong research capabilities', TRUE),
    ('Youth Bridge Europe', 'France', 'NGO', ARRAY['Cultural Exchange', 'Language Learning', 'European Citizenship'], 'FR-BRIDGE-005', 'europe@youthbridge.fr', 'https://youthbridge.fr', 7, 'Extensive experience in cross-cultural youth programs', TRUE),
    ('Tech for Good Initiative', 'Italy', 'Company', ARRAY['Digital Transformation', 'Social Innovation', 'Accessibility'], 'IT-TECH-006', 'partnerships@techforgood.it', 'https://techforgood.it', 6, 'Private sector expertise in technology for social impact', TRUE)
ON CONFLICT (erasmus_code) DO NOTHING;

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
CREATE TRIGGER update_application_sections_updated_at BEFORE UPDATE ON application_sections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to clean up old sessions (run periodically)
CREATE OR REPLACE FUNCTION cleanup_old_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions 
    WHERE last_active < NOW() - INTERVAL '7 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON DATABASE open_horizon_ai IS 'Open Horizon AI - Erasmus+ Project Management System Database';
COMMENT ON TABLE projects IS 'Erasmus+ project information with status tracking';
COMMENT ON TABLE partners IS 'European partner organizations for Erasmus+ projects';
COMMENT ON TABLE application_sections IS 'Generated application content with compliance tracking';
COMMENT ON TABLE partner_searches IS 'Search history and caching for partner discovery';
COMMENT ON TABLE user_sessions IS 'Session management for CLI and API users';