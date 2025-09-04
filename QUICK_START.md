# 🚀 Open Horizon AI - Quick Start Guide

**Erasmus+ Project Management System with Full Web Interface**

## ⚡ 1-Minute Setup

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key
- Supabase account (optional, but recommended)

### Quick Launch

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/odin2-hash/open-horizon-ai.git
   cd open-horizon-ai
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Launch everything:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - 🌐 **Web Interface**: http://localhost:3030
   - 📚 **API Docs**: http://localhost:8080/docs
   - ❤️ **Health Check**: http://localhost:8080/api/health

## 🔧 Port Configuration

**No conflicts with Archon!** Open Horizon AI uses different ports:

| Service | Open Horizon AI | Archon | Purpose |
|---------|----------------|---------|----------|
| Frontend | **3030** | 3737 | React Web UI |
| Backend | **8080** | 8181 | FastAPI Server |
| Database | External | External | Supabase |

## 🎯 Core Features Available

### 💡 **Brainstorming Page** (http://localhost:3030)
- AI-powered Erasmus+ project concept generation
- Focus area selection (Digital, Green, Inclusion)
- Innovation angle development
- Feasibility scoring

### 📋 **Planning Page** (http://localhost:3030/planning)
- Project timeline creation
- Budget estimation and breakdown
- Activity planning with milestones
- Risk assessment tools

### 🤝 **Partners Page** (http://localhost:3030/partners) 
- European partner discovery
- Compatibility scoring (1-10)
- Organization type filtering
- Contact information management

### 📚 **Knowledge Base** (http://localhost:3030/knowledge)
- Erasmus+ Programme Guide search
- Best practices database
- Funding opportunity alerts
- Automated content crawling

## 🔧 Development Mode

If you prefer to run services separately for development:

```bash
# Terminal 1 - Backend
python3 backend/api/main.py

# Terminal 2 - Frontend  
cd frontend
npm install
PORT=3030 npm run dev
```

## 🗄️ Database Setup (Optional)

For full functionality, set up Supabase:

1. Create project at https://supabase.com
2. Run the SQL scripts in `supabase/` directory in order:
   - `simple_setup.sql`
   - `add_indexes.sql` 
   - `add_rls_policies.sql`
   - `add_functions.sql`
   - `add_sample_data.sql`
3. Add your Supabase credentials to `.env`

Without Supabase, the system runs with mock data for development.

## 🚨 Troubleshooting

### Port Conflicts
If you get port conflict errors, check if Archon is running:
```bash
docker ps | grep archon
```

### Container Issues  
```bash
# Rebuild containers
docker-compose down
docker-compose up --build --force-recreate

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

### API Connection Issues
- Verify backend is running: http://localhost:8080/api/health
- Check CORS settings in `.env`
- Ensure OpenAI API key is valid

## 🎓 Usage Examples

### Brainstorming Flow
1. Go to http://localhost:3030
2. Enter project concept: "Digital skills for young refugees"
3. Select focus area: "Digital Transformation"
4. Generate AI suggestions
5. Refine concepts with feasibility scores

### Partner Discovery
1. Navigate to Partners page
2. Search by expertise: "Youth Work, Digital Skills"
3. Filter by countries: Germany, Netherlands
4. View compatibility scores
5. Contact promising partners

### Application Writing
Use the API endpoints to generate content:
```bash
curl -X POST http://localhost:8080/api/application/write \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-project",
    "section_name": "Project Description", 
    "requirements": {"word_limit": 500}
  }'
```

## 🤖 AI Agents Available

- **Brainstorming Agent**: Generates innovative project concepts
- **Planning Agent**: Creates detailed project structures
- **Application Agent**: Writes compliant application text
- **Knowledge Crawler**: Maintains up-to-date Erasmus+ information

## 🌟 What Makes This Special

1. **Complete Archon Fork**: All the polished UI and architecture
2. **Erasmus+ Specialized**: Tailored for European youth projects  
3. **No Conflicts**: Runs alongside Archon perfectly
4. **AI-Powered**: Three specialized agents for the full workflow
5. **Knowledge Base**: Automated crawling of official EU docs
6. **Partner Network**: Real European organization database

## 📞 Support

- 📖 **Full Documentation**: See `README.md`
- 🐛 **Issues**: https://github.com/odin2-hash/open-horizon-ai/issues
- 💬 **Discussions**: GitHub Discussions tab

---

**Ready to revolutionize Erasmus+ project development!** 🚀