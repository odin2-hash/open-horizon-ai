-- Open Horizon AI - Row Level Security Policies
-- Run this after simple_setup.sql and add_indexes.sql

-- Enable Row Level Security
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

-- Settings are readable by authenticated users
CREATE POLICY "Authenticated users can view settings" ON open_horizon_settings
    FOR SELECT TO authenticated USING (true);