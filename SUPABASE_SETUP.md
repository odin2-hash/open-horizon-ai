# Open Horizon AI - Supabase Database Setup

Complete guide for setting up Supabase database for Open Horizon AI, following similar patterns to Archon.

## 🚀 Quick Setup

### 1. Create Supabase Project
1. Go to https://supabase.com and sign in/up
2. Click "New Project"
3. Choose your organization
4. Set project name: `open-horizon-ai`
5. Set database password (save this!)
6. Select region closest to your users
7. Click "Create new project"

### 2. Run Database Setup
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Create a new query
4. Copy and paste the entire contents of `supabase/complete_setup.sql`
5. Click **Run** to execute the script

### 3. Get Your Credentials
From your project dashboard:
- **Project URL**: Found in Settings → API
- **Anon Key**: Found in Settings → API (public key)
- **Service Role Key**: Found in Settings → API (secret key - use the "legacy" longer key)

### 4. Configure Environment
Update your `.env` file:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

## 📋 What Gets Created

### Tables Structure
```
📊 Core Data Tables:
├── projects              # Erasmus+ project information
├── partners             # European partner organizations
├── application_sections # Generated application content
├── project_partners     # Many-to-many project-partner relationships
├── partner_searches     # Search history and caching
├── user_sessions       # Session management
├── erasmus_knowledge   # Knowledge base with vector search
└── open_horizon_settings # Application configuration

🔒 Security:
├── Row Level Security (RLS) policies on all user tables
├── User isolation (users can only see their own data)
└── Public read access to partners and knowledge base
```

### Features Enabled
- ✅ **Vector Search**: Semantic search through Erasmus+ knowledge
- ✅ **Row Level Security**: User data isolation
- ✅ **Automatic Timestamps**: Created/updated tracking
- ✅ **Data Validation**: Check constraints and foreign keys
- ✅ **Sample Data**: Development-ready partner database
- ✅ **Performance Indexes**: Optimized queries
- ✅ **Cleanup Functions**: Maintenance utilities

## 🧪 Testing Your Setup

### 1. Verify Tables Created
In Supabase **Table Editor**:
- You should see 8 tables created
- `partners` table should have 8 sample organizations
- `erasmus_knowledge` should have 4 sample entries

### 2. Test API Connection
```bash
# Test from your application directory
python -c "
from dependencies import OpenHorizonDependencies
from settings import load_settings

settings = load_settings()
deps = OpenHorizonDependencies.from_settings(settings)

# Test connection
try:
    result = deps.supabase.table('partners').select('name').limit(1).execute()
    print('✅ Database connection successful!')
    print(f'Sample partner: {result.data[0][\"name\"]}')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

### 3. Test Vector Search
```sql
-- Run this in Supabase SQL Editor to test vector search
SELECT title, similarity 
FROM match_erasmus_knowledge(
    '[0.1, 0.2, ...]'::vector,  -- Dummy vector (replace with real embedding)
    0.5,  -- Similarity threshold
    3     -- Max results
);
```

## 🔄 Database Management

### Reset Database
If you need to start fresh:
1. Go to SQL Editor in Supabase
2. Copy and paste `supabase/RESET_DB.sql`
3. Run to completely reset the database
4. Then run `complete_setup.sql` again

### Backup Data
```sql
-- Export your projects (run in SQL Editor)
SELECT * FROM projects WHERE user_id = auth.uid();

-- Export your application sections
SELECT * FROM application_sections WHERE user_id = auth.uid();
```

### Add More Sample Data
```sql
-- Add more partner organizations
INSERT INTO partners (name, country, organization_type, expertise_areas, erasmus_code, contact_email, compatibility_score, partnership_rationale, verified)
VALUES 
('Your Organization', 'Your Country', 'NGO', ARRAY['Your', 'Expertise'], 'YOUR-CODE', 'contact@yourorg.com', 8, 'Your rationale', TRUE);

-- Add knowledge base content
INSERT INTO erasmus_knowledge (title, content, source_type, section)
VALUES 
('Custom Knowledge', 'Your custom Erasmus+ knowledge content here', 'custom', 'Custom Section');
```

## 🔒 Security & Privacy

### Row Level Security (RLS)
All user data is protected by RLS policies:
- Users can only access their own projects and data
- Partners and knowledge base are publicly readable
- Service role can bypass RLS for admin functions

### User Authentication
Open Horizon AI integrates with Supabase Auth:
- JWT tokens automatically handled
- User context passed to all database operations
- Session management with automatic cleanup

### Data Privacy
- No sensitive data logged
- API keys stored in environment variables only
- User data isolated per Supabase user account

## 🚨 Troubleshooting

### Common Issues

**1. "relation does not exist" error**
- Make sure you ran `complete_setup.sql` completely
- Check if all tables were created in Table Editor

**2. "insufficient permissions" error**
- Verify you're using the correct service role key
- Check that RLS policies allow your operation

**3. "vector extension not found"**
- Make sure `pgvector` extension is enabled
- Contact Supabase support if extension missing

**4. Connection timeouts**
- Check your network connection
- Verify Supabase project is active (not paused)

### Debug Connection Issues
```bash
# Test basic connection
python -c "
from supabase import create_client
client = create_client('YOUR_URL', 'YOUR_ANON_KEY')
print('Connection test:', client.table('partners').select('count').execute())
"

# Test with service key
python -c "
from supabase import create_client
client = create_client('YOUR_URL', 'YOUR_SERVICE_KEY')
print('Service key test:', client.table('partners').select('count').execute())
"
```

### Performance Optimization
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 📊 Monitoring & Analytics

### Database Metrics (Available in Supabase Dashboard)
- Database size and growth
- Query performance
- Connection usage
- API request patterns

### Custom Analytics Queries
```sql
-- Project creation trends
SELECT DATE(created_at) as date, COUNT(*) as projects_created
FROM projects 
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;

-- Popular partner countries
SELECT country, COUNT(*) as search_count
FROM partner_searches ps
JOIN partners p ON p.country = ANY(ps.required_countries)
WHERE searched_at > NOW() - INTERVAL '30 days'
GROUP BY country
ORDER BY search_count DESC;

-- Application section generation stats
SELECT section_name, 
       COUNT(*) as sections_generated,
       AVG(word_count) as avg_word_count,
       AVG(CASE WHEN compliance_status THEN 1 ELSE 0 END) as compliance_rate
FROM application_sections
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY section_name;
```

## 🔄 Data Migration

### From Development to Production
```sql
-- Export development data
COPY (SELECT * FROM projects) TO '/tmp/projects.csv' WITH CSV HEADER;
COPY (SELECT * FROM partners WHERE verified = true) TO '/tmp/partners.csv' WITH CSV HEADER;

-- Import to production (adjust for your production setup)
\copy projects FROM '/tmp/projects.csv' WITH CSV HEADER;
\copy partners FROM '/tmp/partners.csv' WITH CSV HEADER;
```

### Updating Schema
If you need to modify the schema:
1. Test changes in a development project first
2. Create migration scripts for production
3. Use transactions for safety
4. Consider downtime for major changes

---

## ✅ Setup Checklist

Before going live, verify:
- [ ] Database tables created successfully
- [ ] Sample data loaded
- [ ] Environment variables configured
- [ ] API connection test passes
- [ ] Vector search working
- [ ] RLS policies active
- [ ] User authentication functioning
- [ ] Backup strategy planned

**Your Open Horizon AI database is now ready!** 🎯