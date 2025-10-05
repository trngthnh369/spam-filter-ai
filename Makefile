.PHONY: help install setup train deploy test clean

help:
	@echo "Spam Filter AI - Makefile Commands"
	@echo "===================================="
	@echo "make install      - Install all dependencies"
	@echo "make setup        - Setup project structure"
	@echo "make train        - Run training pipeline"
	@echo "make deploy       - Deploy with Docker"
	@echo "make test         - Run all tests"
	@echo "make clean        - Clean temporary files"
	@echo "make start        - Start services"
	@echo "make stop         - Stop services"
	@echo "make logs         - View logs"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✓ Installation complete"

setup:
	@echo "Setting up project structure..."
	bash scripts/setup.sh
	@echo "✓ Setup complete"

train:
	@echo "Running training pipeline..."
	cd scripts && python run_pipeline.py
	@echo "✓ Training complete"

deploy:
	@echo "Deploying with Docker..."
	bash scripts/deploy.sh

test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test
	@echo "✓ Tests complete"

quick-test:
	@echo "Running quick API tests..."
	bash scripts/quick_test.sh

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf .next node_modules 2>/dev/null || true
	@echo "✓ Cleanup complete"

start:
	docker-compose up -d
	@echo "✓ Services started"

stop:
	docker-compose down
	@echo "✓ Services stopped"

logs:
	docker-compose logs -f

restart: stop start