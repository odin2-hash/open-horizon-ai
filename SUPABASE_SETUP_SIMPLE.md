# Open Horizon AI - Simple Supabase Setup

**Fixed setup guide that works with Supabase SQL Editor**

## 🚀 Step-by-Step Setup

### 1. Create Supabase Project
1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Set project name: `open-horizon-ai`
4. Choose your organization and region
5. Set database password (save this!)
6. Click "Create new project"

### 2. Run SQL Scripts (In Order)

Go to your Supabase project → **SQL Editor** → **New Query**

#### Step 1: Create Tables
Copy and paste the contents of `supabase/simple_setup.sql` and click **Run**

#### Step 2: Add Indexes  
Copy and paste the contents of `supabase/add_indexes.sql` and click **Run**

#### Step 3: Add Security Policies
Copy and paste the contents of `supabase/add_rls_policies.sql` and click **Run**

#### Step 4: Add Functions
Copy and paste the contents of `supabase/add_functions.sql` and click **Run**

#### Step 5: Add Sample Data
Copy and paste the contents of `supabase/add_sample_data.sql` and click **Run**

### 3. Get Your Credentials
From your Supabase project dashboard:
1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (starts with `https://`)
   - **Project API keys**:
     - `anon public` key
     - `service_role secret` key (use the longer one)

### 4. Configure Environment
Update your `.env` file:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

## ✅ Verify Setup

### Check Tables Created
In Supabase **Table Editor**, you should see:
- ✅ `projects` (main project table)
- ✅ `partners` (8 sample organizations)
- ✅ `application_sections` (generated content)
- ✅ `project_partners` (many-to-many relationships)
- ✅ `partner_searches` (search history)
- ✅ `user_sessions` (session management)
- ✅ `open_horizon_settings` (app configuration)

### Test Connection
```bash
python -c "
import os
from supabase import create_client

# Test basic connection
client = create_client(
    os.getenv('SUPABASE_URL'), 
    os.getenv('SUPABASE_KEY')
)

try:
    result = client.table('partners').select('name').limit(1).execute()
    print('✅ Database connection successful!')
    if result.data:
        print(f'Sample partner: {result.data[0][\"name\"]}')
    else:
        print('⚠️ No sample data found - run add_sample_data.sql')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

## 🔧 Manual Alternative (If Scripts Don't Work)

If you have issues with the SQL scripts, you can create tables manually:

### Create Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    focus_area TEXT NOT NULL,
    status TEXT DEFAULT 'brainstorming',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id)
);
```

### Enable RLS
```sql
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own projects" ON projects
    USING (auth.uid() = user_id);
```

### Add Sample Partner
```sql
INSERT INTO partners (name, country, organization_type, expertise_areas)
VALUES ('Test Partner', 'Germany', 'NGO', ARRAY['Digital Skills', 'Youth Work']);
```

## 🚨 Troubleshooting

### Common Issues

**Error: "Unable to find snippet"**
- This means Supabase couldn't parse the SQL
- Try running smaller scripts one at a time
- Use the step-by-step approach above

**Error: "relation does not exist"**
- Make sure you ran `simple_setup.sql` first
- Check Table Editor to see if tables were created

**Error: "permission denied"**
- Check that you're using the service role key
- Verify RLS policies are set up correctly

**Error: "function uuid_generate_v4() does not exist"**
- Run this first: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`

### Alternative Setup Without Scripts

If SQL scripts continue to fail, you can use Supabase's Table Editor:

1. **Go to Table Editor**
2. **Click "Create a new table"**
3. **Create each table manually:**
   - Table name: `projects`
   - Add columns: `id` (uuid), `title` (text), `status` (text), etc.
4. **Enable RLS** in table settings
5. **Add policies** manually

## 📞 Support

If you continue having issues:
1. Check Supabase status page
2. Try creating a fresh Supabase project
3. Use the manual table creation approach
4. Contact Supabase support if needed

The system will work with basic table setup - advanced features can be added later!

## ✅ Minimum Working Setup

At minimum, you need:
```sql
-- Just the essential tables
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    status TEXT DEFAULT 'brainstorming',
    user_id UUID REFERENCES auth.users(id)
);

CREATE TABLE partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    country TEXT NOT NULL
);

-- Enable basic security
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_projects" ON projects USING (auth.uid() = user_id);
```

This minimal setup will get Open Horizon AI working - you can add more features later!