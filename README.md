# Open Horizon AI - Erasmus+ Project Management System

An intelligent Erasmus+ project management system for Swedish NGO "Open Horizon" that streamlines the entire workflow from brainstorming to application submission through specialized AI agents.

## 🎯 Core Features

### 1. Project Brainstorming Assistant 💡
- Interactive AI-guided brainstorming sessions
- Alignment with Erasmus+ priorities (Digital, Green, Inclusion, etc.)
- Feasibility scoring and concept refinement
- Innovation angle development

### 2. Partner & Planning Orchestrator 🤝
- Intelligent European partner discovery
- Compatibility scoring and partnership rationale
- Project structure and timeline generation
- Risk assessment and mitigation planning

### 3. Application Writer ✍️
- Automated generation of compliant application sections
- Real-time compliance checking against Erasmus+ requirements
- Multiple content variations and optimization suggestions
- Evidence-based narrative development

## 🏗️ Architecture

**Complete Web-Based System** (Forked from Archon Architecture):

```
[React Frontend] ↔ [FastAPI Backend] ↔ [Specialized Pydantic AI Agents]
      ↓                    ↓                       ↓
[Modern Web UI]     [REST Endpoints]    [OpenAI GPT-4o-mini]
      ↓                    ↓                       ↓
[User Dashboard]   [Supabase Database]   [Erasmus+ Knowledge Base]
      ↓                    ↓                       ↓
[Real-time Updates] [Web Crawling Service] [Partner Discovery Tools]
```

### Tech Stack
- **Frontend**: React 18 + TypeScript + Tailwind CSS (forked from Archon UI)
- **Backend**: FastAPI with async/await patterns
- **AI Framework**: Pydantic AI with OpenAI GPT-4o-mini
- **Database**: Supabase (PostgreSQL + real-time features + RLS)
- **Knowledge Base**: Web crawling service specialized for Erasmus+ documentation
- **Deployment**: Docker Compose with multi-service orchestration
- **Security**: JWT authentication, Row Level Security, and API key management

## 🚀 Quick Start

### Option 1: Docker (No Repository Clone Needed) 🐳

Deploy instantly without cloning the repository:

```bash
# Download standalone docker-compose
curl -O https://raw.githubusercontent.com/odin2-hash/open-horizon-ai/main/docker-compose.standalone.yml

# Download environment template
curl -O https://raw.githubusercontent.com/odin2-hash/open-horizon-ai/main/.env.example

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section)

# Start application
docker-compose -f docker-compose.standalone.yml up -d
```

**Access:**
- **Web Interface**: http://localhost:3030
- **API Documentation**: http://localhost:8090/docs
- **Health Check**: http://localhost:8090/api/health

For detailed Docker deployment options, see [README-DOCKER.md](README-DOCKER.md).

### Option 2: Development Installation

#### Prerequisites
- Python 3.10+
- OpenAI API key
- Supabase account (recommended for full functionality)

#### Installation

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/odin2-hash/open-horizon-ai.git
   cd open-horizon-ai
   ```

2. **Set up Supabase Database:**
   - Create a new project at https://supabase.com
   - Follow the step-by-step guide in `SUPABASE_SETUP_SIMPLE.md`
   - Run 5 small SQL scripts in order (much more reliable than one large script)
   - This will create all necessary tables, functions, and policies

3. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - LLM_API_KEY: Your OpenAI API key
   # - SUPABASE_URL: Your Supabase project URL
   # - SUPABASE_KEY: Your Supabase anon key
   # - SUPABASE_SERVICE_KEY: Your Supabase service role key (for full functionality)
   ```

6. **Launch the complete system:**
   ```bash
   # Option 1: Docker Compose (Recommended)
   docker-compose up --build
   
   # Option 2: Development mode
   # Terminal 1 - Backend (runs on port 8090)
   python backend/api/main.py
   
   # Terminal 2 - Frontend (runs on port 3030)
   cd frontend && npm install && PORT=3030 npm run dev
   
   # Option 3: Legacy CLI interface
   python cli.py
   ```

7. **Access the application:**
   - **Web Interface**: http://localhost:3030
   - **API Documentation**: http://localhost:8090/docs
   - **Health Check**: http://localhost:8090/api/health
   
   **Note**: Ports have been changed to avoid conflicts with Archon:
   - Open Horizon AI Frontend: **3030** (vs Archon's 3737)
   - Open Horizon AI Backend: **8090** (vs Archon's 8080/8181)

### Environment Variables

```env
# Required
LLM_API_KEY=sk-your-openai-api-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key

# Optional
ERASMUS_PARTNER_DB_API_KEY=your-partner-api-key
SECRET_KEY=your-jwt-secret
DEBUG=false
```

**Important Notes:**
- For cloud Supabase, use the "legacy" (longer) service role key
- The service role key is required for full database functionality including RLS policies
- Without Supabase, the system will work with mock data for development

## 💻 Usage Examples

### CLI Interface

```bash
# Start interactive CLI
python cli.py

# Available options:
# 1. 💡 Brainstorm project ideas
# 2. 🤝 Discover project partners  
# 3. ✍️ Generate application content
# 4. 💬 Chat with AI assistant
# 5. ℹ️ Help and information
```

### Programmatic Usage

```python
from open_horizon_ai import run_open_horizon_agent

# Brainstorm project ideas
response = await run_open_horizon_agent(
    "I want to create a digital skills project for young refugees",
    agent_type="brainstorming"
)

# Find partners
response = await run_open_horizon_agent(
    "Find partners in Germany and Spain for environmental education",
    agent_type="planning"
)

# Generate application content
response = await run_open_horizon_agent(
    "Write the methodology section for our digital inclusion project",
    agent_type="application"
)
```

### API Endpoints

```bash
# Health check
GET http://localhost:8090/api/health

# Brainstorming
POST http://localhost:8090/api/brainstorm
{
  "initial_concept": "Digital skills for young people",
  "focus_preference": "Digital Transformation",
  "organization_context": "Swedish NGO"
}

# Partner search  
POST /api/partners/search
{
  "project_focus": "Environmental education",
  "required_countries": ["Germany", "Spain"],
  "expertise_areas": ["Sustainability", "Youth Work"]
}

# Content generation
POST /api/application/content
{
  "section_type": "Project Description",
  "project_context": {
    "title": "Green Youth Leaders",
    "focus_area": "Green Transition",
    "target_audience": "Young adults 18-25"
  },
  "word_limit": 500
}
```

## 📊 Core Workflow

### Phase 1: Brainstorming 💭
1. **Input**: Initial project concept, focus preferences
2. **Process**: AI analyzes concept against Erasmus+ priorities
3. **Output**: Structured project concepts with feasibility scores
4. **Next**: Partner discovery and planning

### Phase 2: Planning & Partners 🤝
1. **Input**: Selected project concept, geographical preferences
2. **Process**: Partner search, compatibility analysis, structure planning
3. **Output**: Recommended partners with rationale, project timeline
4. **Next**: Application content generation

### Phase 3: Application Writing ✍️
1. **Input**: Project details, section requirements, word limits
2. **Process**: Content generation, compliance checking, optimization
3. **Output**: Polished application text with improvement suggestions
4. **Next**: Review and submission preparation

## 🛠️ Development

### Project Structure

```
open_horizon_ai/
├── __init__.py              # Package exports
├── agent.py                 # Main agent orchestration
├── api.py                   # FastAPI application
├── cli.py                   # Rich CLI interface
├── dependencies.py          # Agent dependencies & context
├── models.py               # Pydantic data models
├── prompts.py              # System prompts for agents
├── providers.py            # Model provider configuration
├── settings.py             # Environment configuration
├── tools.py                # Agent tool implementations
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # Documentation
```

### Key Components

#### Specialized Agents
- **Brainstorming Agent**: Generates project concepts and innovation angles
- **Planning Agent**: Discovers partners and structures project plans  
- **Application Agent**: Writes compliant application text

#### Tool Functions
- `brainstorm_project_ideas()`: Generate structured project concepts
- `discover_erasmus_partners()`: Find compatible European partners
- `generate_application_section()`: Create compliant application text

#### Data Models
- `Project`: Complete project representation
- `Partner`: European organization details
- `ApplicationSection`: Generated content with compliance status

### Testing

```bash
# Install development dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest

# Run with coverage
pytest --cov=open_horizon_ai
```

### Adding New Features

1. **New Tools**: Add functions to `tools.py` with proper error handling
2. **New Models**: Extend `models.py` with Pydantic validation
3. **New Endpoints**: Add routes to `api.py` with proper authentication
4. **New CLI Commands**: Extend workflows in `cli.py`

## 🔒 Security & Compliance

### Data Protection
- API keys stored in environment variables only
- JWT-based authentication for API access
- No sensitive data in logs or error messages
- GDPR-compliant participant data handling

### Erasmus+ Compliance
- Content validation against Programme Guide requirements
- Automatic compliance scoring and feedback
- Partner eligibility verification
- Budget and timeline validation

## 🌍 Localization Support

### Current Languages
- **English**: Primary interface and content generation
- **Swedish**: NGO context awareness and localized guidance

### Future Extensions
- Multi-language interface support
- Content generation in partner country languages
- Regional Erasmus+ programme variations

## 📈 Roadmap

### Phase 1 (Current) ✅
- [x] Core AI agents (brainstorming, planning, application)
- [x] CLI interface with Rich UI
- [x] FastAPI backend with authentication
- [x] Basic partner discovery and content generation
- [x] Supabase integration for data persistence

### Phase 2 (Next)
- [ ] React frontend interface
- [ ] Real-time collaboration features
- [ ] Advanced partner matching algorithms
- [ ] Template library and best practices
- [ ] Integration with Swedish National Agencies

### Phase 3 (Future)
- [ ] Multi-organization support
- [ ] Advanced analytics and success prediction
- [ ] Integration with official Erasmus+ systems
- [ ] Mobile application
- [ ] Multi-language content generation

## 🤝 Contributing

1. Fork the repository from https://github.com/odin2-hash/open-horizon-ai
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes with proper tests
4. Update documentation
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings with examples
- Write tests for new functionality
- Update README for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Open Horizon**: Swedish NGO for project inspiration and requirements
- **Erasmus+ Programme**: For funding opportunities and guidelines
- **Pydantic AI**: For the excellent AI agent framework
- **OpenAI**: For the GPT-4o-mini model powering our agents

## 📞 Support

- **Documentation**: See inline docstrings and CLI help
- **Issues**: Report bugs and feature requests via GitHub issues
- **Repository**: https://github.com/odin2-hash/open-horizon-ai
- **Community**: Join discussions about Erasmus+ project development

---

**Open Horizon AI** - *Transforming Erasmus+ project development through intelligent AI assistance*

Made with ❤️ for the European youth work community