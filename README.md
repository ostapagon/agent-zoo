# Agent Hub

A modern multi-agent system for natural language processing and database interactions, featuring a Text2SQL chatbot with orchestrated agent coordination.

## Project Structure

```
.
├── agents/             # Agent implementations and coordination
│   ├── base/          # Base agent classes and interfaces
│   ├── orchestrator/  # Agent orchestration logic
│   └── text2sql/      # Text2SQL specific agent
├── backend/           # FastAPI backend with Docker support
├── config/            # Configuration files
├── core/              # Core functionality
│   ├── config.py      # Configuration management
│   ├── logging.py     # Logging setup
│   └── utils.py       # Utility functions
├── frontend/          # React + TypeScript frontend
├── models/            # Data models and schemas
├── notebooks/         # Jupyter notebooks for development
├── services/          # Service layer
│   ├── database/      # Database operations and schema
│   └── llm_service.py # LLM integration
├── docker-compose.yml # Docker configuration
└── Makefile          # Build automation
```

## Prerequisites
- Docker Desktop (for PostgreSQL database and services)
- Python 3.9+
- Node.js 18+
- npm (comes with Node.js)
- OpenAI API key

## Quick Start

1. Clone the repository:
```bash
git clone <your-repo-url>
cd agent-zoo
```

2. Start all services with Docker:
```bash
make docker-up
```

Or start services individually:

3. Start the database:
```bash
docker-compose up -d db
```

4. Install dependencies and set up the environment:
```bash
make install
```

5. Start both frontend and backend services:
```bash
make all
```

The application will be available at:
- Frontend: http://localhost (Docker) or http://localhost:5173 (local dev)
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Jupyter Lab: http://localhost:8888 (when running in Docker)

## Available Make Commands

- `make install` - Creates virtual environment and installs all dependencies
- `make all` - Starts both frontend and backend services locally
- `make frontend` - Starts only the frontend service
- `make backend` - Starts only the backend service
- `make docker-up` - Starts all services with Docker
- `make docker-build` - Builds Docker images
- `make docker-down` - Stops Docker services
- `make clean` - Cleans up generated files and virtual environment

## How It Works

### Architecture Overview
The application consists of several key components:

1. **Frontend (React + TypeScript)**
   - Built with React and TypeScript
   - Uses Chakra UI for modern, responsive design
   - Communicates with backend via REST API
   - Real-time chat interface with markdown support

2. **Backend (FastAPI)**
   - RESTful API built with FastAPI
   - Orchestrates the agent system
   - Manages service layer interactions
   - Includes Jupyter Lab for development

3. **Agent System**
   - **Base Agents**: Core agent functionality and interfaces
   - **Text2SQL Agent**: Specialized agent for SQL query generation
   - **Orchestrator**: Manages agent interactions and workflow
   - **Agent Factory**: Creates and manages agent instances

4. **Services Layer**
   - **Database Service**: Handles all database operations
   - **LLM Service**: Manages interactions with language models

5. **Core Components**
   - Configuration management
   - Logging system
   - Utility functions

6. **Database (PostgreSQL)**
   - Stores application data
   - Runs in Docker container
   - Accessible via SQL queries

### Natural Language to SQL Process
1. User inputs a question in natural language
2. Frontend sends the question to the backend
3. Backend routes the request to the Orchestrator
4. Orchestrator determines the appropriate agent (Text2SQL)
5. Text2SQL agent:
   - Uses LLM Service to understand the question
   - Generates appropriate SQL query
   - Validates the query structure
6. Database Service executes the query
7. Results are formatted and sent back through the agent system
8. Frontend displays the results in a user-friendly format

## Development

### Local Development Setup

#### Backend Setup
1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://text2sql:text2sql@localhost:5432/text2sql_db
```

4. Initialize the database:
```bash
cd backend
python init_db.py
```

#### Frontend Setup
1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

### Docker Development
The project includes comprehensive Docker support for development:

- **Multi-service setup**: Database, backend, and frontend containers
- **Volume mounting**: Local code changes reflect immediately in containers
- **Jupyter Lab**: Available at port 8888 for interactive development
- **Health checks**: Ensures services start in the correct order

## API Endpoints

- `POST /api/process` - Process natural language questions
- `GET /api/agents` - Get available agents and capabilities
- `GET /api/health` - Health check endpoint

## Configuration

The system uses YAML-based configuration for agents:

```yaml
coordinator:
  model: gpt-4
  temperature: 0.7
  task_routing:
    sql: text2sql
    query: text2sql
    database: text2sql
```

## Troubleshooting

### Common Issues
- **Docker not running:** Make sure Docker Desktop is started before running `docker-compose`
- **Backend errors:** 
  - Check if virtual environment is activated
  - Verify `.env` file configuration
  - Ensure database is running
- **Frontend issues:**
  - Clear node_modules and run `make install` again
  - Check if port 5173 is available
- **OpenAI errors:** Verify API key validity and quota

### Debugging
- Check backend logs in terminal
- Use browser developer tools for frontend issues
- Check Docker logs: `docker-compose logs`
- Access Jupyter Lab for interactive debugging

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

For any issues or questions, please open an issue or contact the maintainer. 