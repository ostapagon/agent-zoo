.PHONY: all frontend backend install clean venv docker-build docker-down docker-up

# Default target
all:
	@echo "Starting both frontend and backend services..."
	@make frontend & make backend

# Create and activate virtual environment
venv:
	@echo "Setting up virtual environment..."
	@if [ ! -d "venv" ]; then \
		python -m venv venv; \
		echo "Created new virtual environment: venv"; \
	else \
		echo "Virtual environment already exists"; \
	fi
	@echo "To activate the virtual environment, run: source venv/bin/activate"

# Start frontend development server
frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# Start backend server
backend:
	@echo "Starting backend server..."
	cd backend && . ../venv/bin/activate && python main.py

# Start Docker services (FastAPI only)
docker-up:
	@echo "Starting Docker services with FastAPI only..."
	docker-compose up --build

# Build Docker images
docker-build:
	@echo "Building Docker images..."
	docker-compose build

# Stop Docker services
docker-down:
	@echo "Stopping Docker services..."
	docker-compose down


# docker-run-jupyter: docker exec -it agent-zoo-backend-1 jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# Install dependencies for both services
install: venv
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing backend dependencies..."
	. venv/bin/activate && uv pip install -r requirements.txt

# Clean up generated files
clean:
	@echo "Cleaning up..."
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf venv 