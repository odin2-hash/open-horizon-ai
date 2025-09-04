-- Open Horizon AI - Database Functions
-- Run this after other setup scripts

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for auto-updating timestamps
CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_partners_updated_at 
    BEFORE UPDATE ON partners 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_application_sections_updated_at 
    BEFORE UPDATE ON application_sections 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_open_horizon_settings_updated_at 
    BEFORE UPDATE ON open_horizon_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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