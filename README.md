# Shipping & Logistics Management System

## Description
This repository contains a modular backend and management platform for maritime logistics, cargo forwarding, and shipment tracking operations. The system provides core services for consignment lifecycle management, shipment querying and filtering, administrative oversight, user authentication and access control, database migrations, and containerized deployment via Docker.

## Technologies Used
- Python
- FastAPI / Flask
- PostgreSQL / SQLite
- SQLAlchemy & Psycopg2 (ORM & Database Adapters)
- Docker & Docker Compose
- Pydantic & Python-dotenv (Data Validation & Environment Management)
- JWT & Cryptography (Authentication & Role-Based Access Control)
- Jupyter Notebook

## Repository Structure
- `main.py`: Central application entry point orchestrating API routing, middleware, and server execution.
- `auth.py`: Authentication and authorization subsystem handling user registration, token generation, credential verification, and permission validation.
- `admin.py`: Administrative management module and privileged endpoints for system monitoring, user administration, and operational controls.
- `search.py`: Query and search optimization engine facilitating filtering and lookups across shipments, vessels, cargo IDs, and routing schedules.
- `database.py`: Production database connection manager, ORM session factory, and data model mappings.
- `database_local.py`: Local and developmental database configuration for offline execution and isolated testing environments.
- `migration.py`: Schema migration utility managing table instantiation, column alterations, and database synchronization.
- `backup.sql`: SQL database dump containing relational schema definitions and baseline seed data.
- `data/`: Local storage directory for data persistence, runtime files, and auxiliary records.
- `test.ipynb`: Interactive Jupyter Notebook for functional testing, query validation, and exploratory data workflows.
- `Roadmap.docx`: Project architecture, developmental milestones, and specification roadmap.
- `Dockerfile` & `docker-compose.yml`: Container definition and orchestration configuration for consistent multi-container deployments.
- `requirements.txt` & `requirements_lite.txt`: Comprehensive production and lightweight dependency manifests.
- `.env`: Environment configuration file storing secrets, database URIs, API keys, and operational parameters.

## Execution

### Environment Setup
Create and activate an isolated Python virtual environment, then install project dependencies:
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (use requirements_lite.txt for a minimal footprint)
pip install -r requirements.txt
```

### Database Initialization & Migration
Configure environment parameters in .env and execute database setup:
```bash
# Execute database schema creation and migrations
python migration.py

# (Optional) Restore baseline dataset from SQL dump
# PostgreSQL example:
psql -U <username> -d <database_name> -f backup.sql
```

### Running the Application
Start the application server locally:
```bash
python main.py
```

### Docker Deployment
Build and run the containerized application stack using Docker Compose:
```bash
# Build images and start services in the background
docker-compose up --build -d

# Check running container logs
docker-compose logs -f
```