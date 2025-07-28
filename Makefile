# Makefile for Document Intelligence System

.PHONY: help setup install test run clean docker-build docker-run docker-clean

# Default target
help:
	@echo "Document Intelligence System - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup         - Complete system setup"
	@echo "  make install       - Install Python dependencies"
	@echo "  make test          - Run system test"
	@echo ""
	@echo "Run Commands:"
	@echo "  make run INPUT=input.json OUTPUT=output.json"
	@echo "                     - Run the system with specified files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with Docker"
	@echo "  make docker-clean  - Clean Docker resources"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean         - Clean temporary files"

# Setup the complete system
setup:
	@echo "🔧 Setting up Document Intelligence System..."
	python3 -m venv venv || python -m venv venv
	@echo "📦 Installing dependencies..."
	./venv/bin/pip install -r requirements.txt || venv\Scripts\pip install -r requirements.txt
	@echo "📚 Setting up NLTK data..."
	./venv/bin/python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)" || venv\Scripts\python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"
	@echo "✅ Setup complete!"

# Install dependencies only
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "📚 Setting up NLTK data..."
	python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"

# Run system test
test:
	@echo "🧪 Running system test..."
	python run.py test

# Run the system
run:
	@if [ -z "$(INPUT)" ] || [ -z "$(OUTPUT)" ]; then \
		echo "❌ Error: Please specify INPUT and OUTPUT files"; \
		echo "Usage: make run INPUT=input.json OUTPUT=output.json"; \
		exit 1; \
	fi
	@echo "🚀 Running document intelligence system..."
	python main.py $(INPUT) $(OUTPUT)

# Build Docker image
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t doc-intelligence .

# Run with Docker
docker-run:
	@echo "🐳 Running with Docker..."
	docker run -v $(PWD):/app doc-intelligence input.json output.json

# Run with Docker Compose
docker-compose-run:
	@echo "🐳 Running with Docker Compose..."
	mkdir -p input output documents
	docker-compose up document-intelligence

# Development with Docker
docker-dev:
	@echo "🐳 Starting development container..."
	docker-compose up dev

# Clean Docker resources
docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down --rmi all --volumes --remove-orphans || true
	docker rmi doc-intelligence || true
	docker system prune -f

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + || true
	rm -f test_output.json || true

# Install system dependencies (Ubuntu/Debian)
install-system-deps:
	@echo "📦 Installing system dependencies..."
	sudo apt update
	sudo apt install -y python3 python3-pip python3-venv gcc g++

# Create project structure
init:
	@echo "📁 Creating project structure..."
	mkdir -p input output documents logs
	@echo "✅ Project structure created!"

# Validate input file
validate:
	@if [ -z "$(INPUT)" ]; then \
		echo "❌ Error: Please specify INPUT file"; \
		echo "Usage: make validate INPUT=input.json"; \
		exit 1; \
	fi
	@echo "🔍 Validating input file..."
	python -c "import json; json.load(open('$(INPUT)')); print('✅ Valid JSON')"

# Show system info
info:
	@echo "ℹ️  System Information:"
	@echo "Python version: $$(python --version 2>&1)"
	@echo "Current directory: $$(pwd)"
	@echo "Available memory: $$(free -h 2>/dev/null | grep Mem | awk '{print $$2}' || echo 'N/A')"
	@echo "CPU cores: $$(nproc 2>/dev/null || echo 'N/A')"

# Full setup with system dependencies (Ubuntu/Debian only)
full-setup: install-system-deps setup init
	@echo "🎉 Full setup complete!"