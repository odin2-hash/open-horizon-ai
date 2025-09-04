-- Open Horizon AI - Database Reset Script
-- ⚠️ WARNING: This script will delete all data in your Open Horizon AI database
-- Use this script to reset your database to a clean state

-- This script safely removes all tables, functions, triggers, and policies
-- with proper dependency handling, similar to Archon's reset script

DO $$
DECLARE
    _table_name TEXT;
    _function_name TEXT;
    _policy_name TEXT;
    _trigger_name TEXT;
BEGIN
    RAISE NOTICE 'Starting Open Horizon AI database reset...';
    
    -- Drop all RLS policies first
    FOR _policy_name IN 
        SELECT policyname 
        FROM pg_policies 
        WHERE tablename IN ('projects', 'application_sections', 'partner_searches', 'user_sessions')
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON projects CASCADE', _policy_name);
        EXECUTE format('DROP POLICY IF EXISTS %I ON application_sections CASCADE', _policy_name);
        EXECUTE format('DROP POLICY IF EXISTS %I ON partner_searches CASCADE', _policy_name);
        EXECUTE format('DROP POLICY IF EXISTS %I ON user_sessions CASCADE', _policy_name);
        EXECUTE format('DROP POLICY IF EXISTS %I ON partners CASCADE', _policy_name);
        EXECUTE format('DROP POLICY IF EXISTS %I ON erasmus_knowledge CASCADE', _policy_name);
        RAISE NOTICE 'Dropped policy: %', _policy_name;
    END LOOP;
    
    -- Drop all triggers
    FOR _trigger_name IN 
        SELECT trigger_name 
        FROM information_schema.triggers 
        WHERE trigger_schema = current_schema()
        AND event_object_table IN (
            'projects', 'partners', 'application_sections', 
            'erasmus_knowledge', 'open_horizon_settings'
        )
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON projects CASCADE', _trigger_name);
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON partners CASCADE', _trigger_name);
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON application_sections CASCADE', _trigger_name);
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON erasmus_knowledge CASCADE', _trigger_name);
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON open_horizon_settings CASCADE', _trigger_name);
        RAISE NOTICE 'Dropped trigger: %', _trigger_name;
    END LOOP;
    
    -- Drop tables in correct dependency order
    DROP TABLE IF EXISTS user_sessions CASCADE;
    RAISE NOTICE 'Dropped table: user_sessions';
    
    DROP TABLE IF EXISTS partner_searches CASCADE;
    RAISE NOTICE 'Dropped table: partner_searches';
    
    DROP TABLE IF EXISTS application_sections CASCADE;
    RAISE NOTICE 'Dropped table: application_sections';
    
    DROP TABLE IF EXISTS project_partners CASCADE;
    RAISE NOTICE 'Dropped table: project_partners';
    
    DROP TABLE IF EXISTS projects CASCADE;
    RAISE NOTICE 'Dropped table: projects';
    
    DROP TABLE IF EXISTS partners CASCADE;
    RAISE NOTICE 'Dropped table: partners';
    
    DROP TABLE IF EXISTS erasmus_knowledge CASCADE;
    RAISE NOTICE 'Dropped table: erasmus_knowledge';
    
    DROP TABLE IF EXISTS open_horizon_settings CASCADE;
    RAISE NOTICE 'Dropped table: open_horizon_settings';
    
    -- Drop custom functions
    DROP FUNCTION IF EXISTS match_erasmus_knowledge(vector, float, int) CASCADE;
    RAISE NOTICE 'Dropped function: match_erasmus_knowledge';
    
    DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
    RAISE NOTICE 'Dropped function: update_updated_at_column';
    
    DROP FUNCTION IF EXISTS cleanup_old_data() CASCADE;
    RAISE NOTICE 'Dropped function: cleanup_old_data';
    
    -- Drop custom types
    DROP TYPE IF EXISTS project_status CASCADE;
    RAISE NOTICE 'Dropped type: project_status';
    
    DROP TYPE IF EXISTS organization_type CASCADE;
    RAISE NOTICE 'Dropped type: organization_type';
    
    RAISE NOTICE '✅ Open Horizon AI database reset completed successfully!';
    RAISE NOTICE 'All tables, functions, triggers, policies, and custom types have been removed.';
    RAISE NOTICE 'You can now run complete_setup.sql to recreate the database schema.';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '❌ Error during reset: %', SQLERRM;
        RAISE EXCEPTION 'Database reset failed: %', SQLERRM;
END $$;