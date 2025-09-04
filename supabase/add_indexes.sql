-- Open Horizon AI - Add Indexes and Performance Optimizations
-- Run this after simple_setup.sql

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_focus_area ON projects(focus_area);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);

CREATE INDEX IF NOT EXISTS idx_partners_country ON partners(country);
CREATE INDEX IF NOT EXISTS idx_partners_organization_type ON partners(organization_type);
CREATE INDEX IF NOT EXISTS idx_partners_expertise_areas ON partners USING GIN(expertise_areas);
CREATE INDEX IF NOT EXISTS idx_partners_erasmus_code ON partners(erasmus_code) WHERE erasmus_code IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_application_sections_project_id ON application_sections(project_id);
CREATE INDEX IF NOT EXISTS idx_application_sections_section_name ON application_sections(section_name);
CREATE INDEX IF NOT EXISTS idx_application_sections_user_id ON application_sections(user_id);

CREATE INDEX IF NOT EXISTS idx_partner_searches_project_id ON partner_searches(project_id);
CREATE INDEX IF NOT EXISTS idx_partner_searches_user_id ON partner_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_partner_searches_searched_at ON partner_searches(searched_at);

CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_active ON user_sessions(last_active);