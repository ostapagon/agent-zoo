# Docker Setup for Agent Chat Application

This project is now containerized with Docker, providing a consistent development and deployment environment.

## Prerequisites

1. **Docker Desktop** - Make sure Docker Desktop is installed and running
   - Download from: https://www.docker.com/products/docker-desktop/
   - Start Docker Desktop before running any Docker commands

2. **Docker Compose** - Usually comes with Docker Desktop

## Quick Start

1. **Start Docker Desktop** (if not already running)

2. **Build and run all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000
   - Database: localhost:5432

## Architecture

The application consists of three main services:

### 1. PostgreSQL Database (`db`)
- **Image**: postgres:15
- **Port**: 5432
- **Database**: text2sql_db
- **User**: text2sql
- **Password**: text2sql
- **Data Persistence**: Uses Docker volume `postgres_data`

### 2. Backend API (`backend`)
- **Technology**: FastAPI (Python)
- **Port**: 8000
- **Features**:
  - RESTful API endpoints
  - Agent coordination
  - Database connectivity
  - Health checks
- **Dependencies**: Waits for database to be healthy

### 3. Frontend Web App (`frontend`)
- **Technology**: React + TypeScript + Vite
- **Port**: 80
- **Features**:
  - Modern UI with Chakra UI
  - API proxy through nginx
  - Static file serving
  - CORS handling
- **Dependencies**: Waits for backend to be ready

## Service Communication

- **Frontend ↔ Backend**: API calls proxied through nginx
- **Backend ↔ Database**: Direct PostgreSQL connection
- **All services**: Connected via Docker network `app-network`

## Development Workflow

### Running in Development Mode
```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Service Development
```bash
# Rebuild specific service
docker-compose build backend

# Run only backend
docker-compose up backend

# Access container shell
docker-compose exec backend bash
```

### Database Operations
```bash
# Connect to database
docker-compose exec db psql -U text2sql -d text2sql_db

# View database logs
docker-compose logs db
```

## Environment Variables

The following environment variables are configured:

- `DATABASE_URL`: PostgreSQL connection string
- `PYTHONPATH`: Python path for the backend
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

## Health Checks

All services include health checks:
- **Database**: Checks if PostgreSQL is ready to accept connections
- **Backend**: Checks if the API health endpoint responds
- **Frontend**: Checks if nginx is serving content

## Troubleshooting

### Common Issues

1. **Docker Desktop not running**
   - Start Docker Desktop application
   - Wait for it to fully initialize

2. **Port conflicts**
   - Ensure ports 80, 8000, and 5432 are not in use
   - Modify ports in docker-compose.yml if needed

3. **Build failures**
   - Clear Docker cache: `docker system prune -a`
   - Rebuild without cache: `docker-compose build --no-cache`

4. **Database connection issues**
   - Check if database container is healthy: `docker-compose ps`
   - View database logs: `docker-compose logs db`

### Useful Commands

```bash
# View all containers
docker-compose ps

# View service logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]

# Remove all containers and volumes
docker-compose down -v

# View resource usage
docker stats
```

## Production Considerations

For production deployment:

1. **Environment Variables**: Use `.env` files or external secret management
2. **SSL/TLS**: Configure nginx with SSL certificates
3. **Database**: Use managed PostgreSQL service or configure backups
4. **Monitoring**: Add logging and monitoring solutions
5. **Security**: Review and harden container security settings

## File Structure

```
agent-chat/
├── docker-compose.yml          # Main orchestration file
├── .dockerignore              # Global Docker ignore rules
├── backend/
│   ├── Dockerfile             # Backend container definition
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── Dockerfile             # Frontend container definition
│   ├── nginx.conf             # Nginx configuration
│   └── .dockerignore          # Frontend-specific ignore rules
└── README-Docker.md           # This file
```

For more detailed commands and examples, see `docker-commands.md`. 