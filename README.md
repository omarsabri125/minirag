# MiniRAG

A flexible and scalable Retrieval-Augmented Generation (RAG) system supporting multiple LLM providers and vector databases.

## 🌟 Features

- **Multiple LLM Providers**: OpenAI and Cohere integration
- **Flexible Vector Databases**: Support for Qdrant and pgvector
- **Robust Data Storage**: PostgreSQL for storing documents, chunks, and metadata
- **ORM Integration**: SQLAlchemy for database schema management and queries
- **Migration Support**: Alembic for database schema versioning and evolution
- **Chunk Management**: Intelligent document chunking and storage
- **Containerized**: Docker support for easy deployment
- **Provider Factory Pattern**: Easy switching between providers
- **Modular Architecture**: Clean separation of concerns

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Database Architecture](#database-architecture)
- [Usage](#usage)
- [Database Migrations](#database-migrations)
- [Docker Setup](#docker-setup)
- [Supported Providers](#supported-providers)

## 🔧 Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL 13+
- API keys for chosen LLM provider (OpenAI/Cohere)
- Qdrant (optional, if not using pgvector)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/minirag.git
cd minirag
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/minirag_db

# LLM Provider Configuration
LLM_PROVIDER=openai  # or 'cohere'
OPENAI_API_KEY=your_openai_api_key_here
COHERE_API_KEY=your_cohere_api_key_here

# Vector Database Configuration
VECTOR_DB=qdrant  # or 'pgvector'
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key  # optional

# Application Settings
LOG_LEVEL=INFO
```

## 📁 Project Structure

```
minirag/
├── src/
│   ├── routes/          # API routes and endpoints
│   ├── stores/          # Vector store implementations
│   │   └── llm/         # LLM provider management
│   │       ├── providers/      # Individual LLM implementations
│   │       ├── templates/      # Prompt templates
│   │       ├── LLMEnums.py
│   │       ├── LLMInterface.py
│   │       └── LLMProviderFactory.py
│   ├── vectordb/        # Vector database implementations
│   │   ├── providers/          # Vector DB implementations
│   │   ├── VectorDBEnums.py
│   │   ├── VectorDBInterface.py
│   │   └── VectorDBProviderFactory.py
│   ├── models/          # SQLAlchemy ORM models
│   │   ├── document.py         # Document model
│   │   ├── chunk.py            # Chunk model
│   │   └── collection.py       # Collection model
│   └── database/        # Database configuration and sessions
├── alembic/             # Database migration scripts
│   ├── versions/               # Migration versions
│   └── env.py                  # Alembic environment config
├── .env                 # Environment variables (not in git)
├── .env.example         # Example environment configuration
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── logger.py            # Logging configuration
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies
```

## 🗃️ Database Architecture

### Overview

MiniRAG uses a hybrid storage approach combining PostgreSQL and vector databases for optimal performance:

- **PostgreSQL**: Stores original documents, text chunks, and metadata
- **Vector Database** (Qdrant/pgvector): Stores embeddings for semantic search
- **SQLAlchemy**: Manages database schema and relationships
- **Alembic**: Handles schema migrations

### Data Models

#### Documents Table
Stores the original documents uploaded to the system:
- Document ID (primary key)
- Title
- Full content
- Source URL/reference
- Metadata (JSON field for flexible attributes)
- Collection association
- Timestamps (created_at, updated_at)

#### Chunks Table
Stores text chunks extracted from documents:
- Chunk ID (primary key)
- Document ID (foreign key)
- Chunk content (text)
- Chunk index (position in document)
- Embedding ID (reference to vector database)
- Token count
- Chunk-specific metadata

#### Collections Table
Groups related documents together:
- Collection ID (primary key)
- Collection name
- Description
- Created timestamp
- Associated documents

### Data Flow

1. **Document Upload**: Original document stored in PostgreSQL documents table
2. **Chunking**: Document split into smaller chunks, stored in chunks table
3. **Embedding Generation**: LLM provider generates vector embeddings for each chunk
4. **Vector Storage**: Embeddings stored in vector database (Qdrant or pgvector)
5. **Linking**: Chunk records updated with embedding IDs to maintain relationship
6. **Query Processing**: 
   - User query converted to embedding
   - Vector database finds similar embeddings
   - PostgreSQL retrieves corresponding chunk content and metadata
   - LLM generates response using retrieved context

### Chunking Strategy

MiniRAG implements intelligent document chunking:
- **Fixed-size chunking**: Configurable token-based splitting (default: 512 tokens)
- **Overlap**: Chunks overlap to maintain context (default: 50 tokens)
- **Semantic preservation**: Attempts to split at natural boundaries (paragraphs, sentences)
- **Metadata retention**: Each chunk maintains reference to parent document

### SQLAlchemy Integration

SQLAlchemy provides:
- **Object-Relational Mapping**: Database tables mapped to Python classes
- **Relationship Management**: Automatic handling of foreign keys and joins
- **Query Building**: Pythonic interface for database queries
- **Type Safety**: Python type hints for database fields
- **JSON Field Support**: Native handling of metadata fields

## 💻 Usage

### Running the Application

#### Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run database migrations
alembic upgrade head

# Start the application
python main.py
```

#### Using Docker

```bash
# Build and start all services
docker-compose up -d

# Run migrations
docker-compose exec minirag-app alembic upgrade head

# View logs
docker-compose logs -f minirag-app

# Stop services
docker-compose down
```

### Workflow Overview

1. **Initialize**: Application connects to PostgreSQL and vector database
2. **Upload Documents**: Documents stored in PostgreSQL with metadata
3. **Process**: Documents automatically chunked and embedded
4. **Query**: User queries matched against vector embeddings
5. **Retrieve**: Relevant chunks fetched from PostgreSQL
6. **Generate**: LLM generates response using retrieved context

## 🗄️ Database Migrations

### Alembic Migration Management

Alembic tracks and manages database schema changes over time.

#### Initial Setup

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Configure alembic.ini with your database URL
```

#### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user preferences table"

# Create empty migration for manual changes
alembic revision -m "Add custom indexes"
```

#### Applying Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade by specific number of revisions
alembic upgrade +2

# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

#### Migration History

```bash
# View current database version
alembic current

# View migration history
alembic history

# View detailed history with messages
alembic history --verbose
```

#### Best Practices

- Always review auto-generated migrations before applying
- Test migrations on development database first
- Create database backups before production migrations
- Use descriptive migration messages
- Keep migrations small and focused

## 🐳 Docker Setup

### Docker Compose Services

The application includes three main services:

#### PostgreSQL Service
- **Image**: PostgreSQL 15 Alpine
- **Purpose**: Stores documents, chunks, and metadata
- **Port**: 5432
- **Volume**: Persistent storage for database files
- **Health Check**: Ensures database is ready before app starts

#### Qdrant Service (Optional)
- **Image**: Latest Qdrant
- **Purpose**: Vector similarity search
- **Port**: 6333
- **Volume**: Persistent storage for vector data

#### MiniRAG Application
- **Build**: Custom Dockerfile
- **Purpose**: Main application service
- **Port**: 8000
- **Dependencies**: Waits for PostgreSQL health check

### Docker Commands

```bash
# Build services
docker-compose build

# Start services in background
docker-compose up -d

# Start services with live logs
docker-compose up

# View logs for specific service
docker-compose logs -f minirag-app
docker-compose logs -f postgres

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart specific service
docker-compose restart minirag-app

# Execute commands in running container
docker-compose exec minirag-app bash
docker-compose exec postgres psql -U minirag_user -d minirag_db
```

### Running Migrations in Docker

```bash
# Run migrations
docker-compose exec minirag-app alembic upgrade head

# Create new migration
docker-compose exec minirag-app alembic revision --autogenerate -m "Description"

# Check migration status
docker-compose exec minirag-app alembic current
```

### Environment-Specific Deployments

```bash
# Development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

# Testing environment
docker-compose -f docker-compose.yml -f docker-compose.test.yml up
```

## 🔌 Supported Providers

### LLM Providers

#### OpenAI
- **Models**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **Capabilities**: Text generation, embeddings, chat completions
- **Configuration**: Requires OPENAI_API_KEY
- **Use Cases**: General-purpose text generation, high-quality embeddings

#### Cohere
- **Models**: Command, Command-light, Embed
- **Capabilities**: Text generation, embeddings, reranking
- **Configuration**: Requires COHERE_API_KEY
- **Use Cases**: Multilingual support, semantic reranking

### Vector Databases

#### Qdrant
- **Type**: Dedicated vector search engine
- **Deployment**: Cloud-hosted or self-hosted
- **Features**: 
  - High-performance similarity search
  - Payload filtering
  - Real-time indexing
  - Horizontal scaling
- **Configuration**: Requires QDRANT_URL
- **Best For**: Large-scale deployments, high-throughput applications

#### pgvector
- **Type**: PostgreSQL extension
- **Deployment**: Integrated with PostgreSQL
- **Features**:
  - Native PostgreSQL integration
  - ACID compliance
  - Familiar SQL interface
  - Simpler infrastructure
- **Configuration**: Automatic with DATABASE_URL
- **Best For**: Smaller deployments, simplified architecture

## 🛠️ Configuration

### Environment Variables

All configuration is managed through environment variables in the `.env` file:

- **DATABASE_URL**: PostgreSQL connection string
- **LLM_PROVIDER**: Choice of LLM provider (openai, cohere)
- **VECTOR_DB**: Choice of vector database (qdrant, pgvector)
- **API Keys**: Provider-specific authentication
- **LOG_LEVEL**: Application logging verbosity

### Provider Selection

Switch between providers by changing environment variables - no code changes required:

```bash
# Use OpenAI with Qdrant
LLM_PROVIDER=openai
VECTOR_DB=qdrant

# Use Cohere with pgvector
LLM_PROVIDER=cohere
VECTOR_DB=pgvector
```

## 📊 Logging

The application includes comprehensive logging:

- **File**: Detailed logs written to log files
- **Console**: Colored console output for development
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Configuration**: Managed through `logger.py`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/test_llm_providers.py

# Run tests with verbose output
pytest -v
```
## 🙏 Acknowledgments

- **OpenAI**: GPT models and embeddings API
- **Cohere**: Language models and embedding services
- **Qdrant**: High-performance vector search engine
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool

## 📧 Support

For questions, issues, or feature requests:

- Open an issue on GitHub
- Check existing documentation
- Review closed issues for solutions

## 🔐 Security

- Never commit `.env` files or API keys
- Use environment variables for sensitive data
- Rotate API keys regularly
- Keep dependencies updated
- Review security advisories

---

**MiniRAG** - Flexible RAG system with multi-provider support