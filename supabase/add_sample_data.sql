-- Open Horizon AI - Sample Data
-- Run this after the other setup scripts

-- Insert application settings
INSERT INTO open_horizon_settings (setting_name, setting_value, description) VALUES
    ('app_version', '1.0.0', 'Application version'),
    ('default_language', 'en', 'Default language for the application'),
    ('organization_name', 'Open Horizon', 'Default organization name'),
    ('organization_country', 'Sweden', 'Default organization country'),
    ('erasmus_program_year', '2024', 'Current Erasmus+ programme year')
ON CONFLICT (setting_name) DO NOTHING;

-- Insert sample partner organizations
INSERT INTO partners (name, country, organization_type, expertise_areas, erasmus_code, contact_email, contact_website, compatibility_score, partnership_rationale, verified) 
VALUES 
    ('Digital Youth Foundation', 'Germany', 'NGO', ARRAY['Digital Skills', 'Youth Work', 'Innovation'], 'DE-YOUTH-001', 'contact@digitalyouth.de', 'https://digitalyouth.de', 9, 'Strong digital expertise and proven track record in youth projects', true),
    ('Green Action Network', 'Netherlands', 'NGO', ARRAY['Environmental Education', 'Sustainability', 'Community Engagement'], 'NL-GREEN-002', 'info@greenaction.nl', 'https://greenaction.nl', 8, 'Excellent environmental focus with European-wide networks', true),
    ('Inclusion Works', 'Spain', 'Public Body', ARRAY['Social Inclusion', 'Diversity Training', 'Youth Support'], 'ES-INCL-003', 'hello@inclusionworks.es', 'https://inclusionworks.es', 7, 'Specialized in inclusion work with vulnerable groups', true),
    ('Innovation Academy', 'Finland', 'Higher Education Institution', ARRAY['Innovation', 'Entrepreneurship', 'Technology'], 'FI-INNOV-004', 'partnerships@innovacademy.fi', 'https://innovacademy.fi', 8, 'Academic excellence in innovation and strong research capabilities', true),
    ('Youth Bridge Europe', 'France', 'NGO', ARRAY['Cultural Exchange', 'Language Learning', 'European Citizenship'], 'FR-BRIDGE-005', 'europe@youthbridge.fr', 'https://youthbridge.fr', 7, 'Extensive experience in cross-cultural youth programs', true),
    ('Tech for Good Initiative', 'Italy', 'Company', ARRAY['Digital Transformation', 'Social Innovation', 'Accessibility'], 'IT-TECH-006', 'partnerships@techforgood.it', 'https://techforgood.it', 6, 'Private sector expertise in technology for social impact', true),
    ('Nordic Youth Collective', 'Norway', 'NGO', ARRAY['Youth Participation', 'Democratic Values', 'Nordic Cooperation'], 'NO-NORDIC-007', 'contact@nordicyouth.no', 'https://nordicyouth.no', 8, 'Strong Nordic perspective and democratic participation focus', true),
    ('Baltic Innovation Hub', 'Estonia', 'Public Body', ARRAY['Digital Innovation', 'Startups', 'E-governance'], 'EE-BALTIC-008', 'partnerships@baltichub.ee', 'https://baltichub.ee', 7, 'Digital innovation expertise from one of Europe''s most digital societies', true)
ON CONFLICT (erasmus_code) DO NOTHING;