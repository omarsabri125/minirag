# MiniRAG
A flexible and scalable Retrieval-Augmented Generation (RAG) system supporting multiple LLM providers, vector databases, and advanced search capabilities.

## 🌟 Features

- **Multiple LLM Providers**: OpenAI and Cohere integration
- **Flexible Vector Databases**: Support for Qdrant and pgvector
- **Advanced Search Capabilities**:
  - **Hybrid Search**: Combines semantic (vector) and keyword (BM25) search for optimal retrieval
  - **Query Expansion**: Automatically generates query variations to improve recall
  - **Semantic Cache**: Caches similar queries to reduce API calls and improve response time
  - **Document Reranking**: Reorders retrieved documents by relevance using LLM-based scoring
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
- [Advanced Features](#advanced-features)
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

# Search Configuration
ENABLE_HYBRID_SEARCH=true
HYBRID_SEARCH_ALPHA=0.5  # Weight between semantic (0.0) and keyword (1.0) search
ENABLE_QUERY_EXPANSION=true
QUERY_EXPANSION_COUNT=3  # Number of query variations to generate
ENABLE_SEMANTIC_CACHE=true
CACHE_SIMILARITY_THRESHOLD=0.95  # Threshold for cache hit
ENABLE_RERANKING=true
RERANK_TOP_K=10  # Number of documents to rerank

# Application Settings
LOG_LEVEL=INFO
```

## 📁 Project Structure

```
minirag/
├── src/
│   ├── routes/                    # API routes and endpoints
│   ├── stores/                    # Vector store implementations
│   │   └── llm/                   # LLM provider management
│   │       ├── providers/         # Individual LLM implementations
│   │       ├── templates/         # Prompt templates
│   │       ├── LLMEnums.py
│   │       ├── LLMInterface.py
│   │       └── LLMProviderFactory.py
│   ├── vectordb/                  # Vector database implementations
│   │   ├── providers/             # Vector DB implementations
│   │   ├── VectorDBEnums.py
│   │   ├── VectorDBInterface.py
│   │   └── VectorDBProviderFactory.py
│   ├── search/                    # Advanced search features
│   │   ├── hybrid_search.py       # Hybrid search implementation
│   │   ├── query_expansion.py     # Query expansion logic
│   │   ├── semantic_cache.py      # Semantic caching system
│   │   └── reranker.py            # Document reranking
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── document.py            # Document model
│   │   ├── chunk.py               # Chunk model
│   │   ├── collection.py          # Collection model
│   │   └── cache_entry.py         # Semantic cache model
│   └── database/                  # Database configuration and sessions
├── alembic/                       # Database migration scripts
│   ├── versions/                  # Migration versions
│   └── env.py                     # Alembic environment config
├── .env                           # Environment variables (not in git)
├── .env.example                   # Example environment configuration
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── logger.py                      # Logging configuration
├── main.py                        # Application entry point
└── requirements.txt               # Python dependencies
```

## 🗃️ Database Architecture

### Overview
MiniRAG uses a hybrid storage approach combining PostgreSQL and vector databases for optimal performance:

- **PostgreSQL**: Stores original documents, text chunks, metadata, and semantic cache
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
- BM25 scores (for keyword search)

#### Collections Table
Groups related documents together:
- Collection ID (primary key)
- Collection name
- Description
- Created timestamp
- Associated documents

#### Cache Entries Table
Stores semantic cache for query optimization:
- Cache ID (primary key)
- Query text
- Query embedding
- Response content
- Metadata (context, parameters)
- Hit count
- Last accessed timestamp
- Created timestamp

### Data Flow

1. **Document Upload**: Original document stored in PostgreSQL documents table
2. **Chunking**: Document split into smaller chunks, stored in chunks table
3. **Embedding Generation**: LLM provider generates vector embeddings for each chunk
4. **Vector Storage**: Embeddings stored in vector database (Qdrant or pgvector)
5. **Linking**: Chunk records updated with embedding IDs to maintain relationship
6. **Query Processing**:
   - Check semantic cache for similar queries
   - Expand query if enabled (generate query variations)
   - Perform hybrid search (combine semantic and keyword search)
   - Rerank retrieved documents by relevance
   - LLM generates response using top-ranked context
   - Cache response for future similar queries

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

## 🚀 Advanced Features

### 1. Hybrid Search

Hybrid search combines semantic (vector-based) and keyword (BM25) search to leverage the strengths of both approaches:

**How it works:**
- **Semantic Search**: Finds documents with similar meanings using vector embeddings
- **Keyword Search**: Finds documents with exact term matches using BM25 algorithm
- **Score Fusion**: Combines scores using configurable alpha parameter (0.0 = pure semantic, 1.0 = pure keyword)

**Benefits:**
- Better recall for specific terminology and proper nouns
- Improved semantic understanding for conceptual queries
- Balanced results that capture both exact matches and related concepts

**Configuration:**
```env
ENABLE_HYBRID_SEARCH=true
HYBRID_SEARCH_ALPHA=0.5  # Adjust weight between semantic and keyword
```

**Usage:**
```python
# Automatic hybrid search when querying
results = rag_system.query(
    "What are transformer models?",
    search_type="hybrid",
    alpha=0.5
)
```

### 2. Query Expansion

Query expansion automatically generates variations of the user's query to improve retrieval coverage:

**How it works:**
- Takes original user query
- Uses LLM to generate semantically similar query variations
- Performs search with all query versions
- Merges and deduplicates results

**Benefits:**
- Captures different phrasings of the same question
- Improves recall for ambiguous queries
- Handles terminology variations

**Configuration:**
```env
ENABLE_QUERY_EXPANSION=true
QUERY_EXPANSION_COUNT=3  # Number of variations to generate
```

**Example:**
```
Original query: "How to train neural networks?"

Expanded queries:
1. "What are the methods for training deep learning models?"
2. "Neural network training techniques and best practices"
3. "Step-by-step guide to training artificial neural networks"
```

### 3. Semantic Cache

Semantic cache stores previous query results and returns cached responses for similar queries:

**How it works:**
- Query is converted to embedding
- System checks cache for similar query embeddings
- If similarity exceeds threshold, returns cached response
- Otherwise, performs full retrieval and caches new result

**Benefits:**
- Reduces API calls to LLM providers (cost savings)
- Faster response times for common queries
- Improved system efficiency

**Configuration:**
```env
ENABLE_SEMANTIC_CACHE=true
CACHE_SIMILARITY_THRESHOLD=0.95  # Cosine similarity threshold
```

**Cache Management:**
```python
# Cache is automatically managed
# View cache statistics
cache_stats = rag_system.get_cache_statistics()

# Clear cache if needed
rag_system.clear_cache(older_than_days=7)
```

### 4. Document Reranking

Reranking reorders retrieved documents using LLM-based relevance scoring:

**How it works:**
- Initial retrieval returns top N documents (e.g., top 20)
- Reranker uses LLM to score each document's relevance to query
- Documents reordered by relevance scores
- Top K documents used for generation (e.g., top 5)

**Benefits:**
- Improves precision of retrieved context
- Better handles complex queries requiring deep understanding
- Reduces noise in context sent to generation LLM

**Configuration:**
```env
ENABLE_RERANKING=true
RERANK_TOP_K=10  # Number of documents to rerank
```

**Reranking Models:**
- OpenAI: Uses GPT-based relevance scoring
- Cohere: Uses dedicated Rerank API endpoint

**Usage:**
```python
results = rag_system.query(
    "Explain attention mechanisms",
    retrieve_k=20,  # Retrieve 20 documents
    rerank_top_k=5  # Rerank and use top 5
)
```

### Complete Search Pipeline

When all features are enabled, the search pipeline works as follows:

```
User Query
    ↓
1. Check Semantic Cache
    ↓ (cache miss)
2. Query Expansion (generate 3 variations)
    ↓
3. Hybrid Search (semantic + keyword, alpha=0.5)
    ↓ (retrieve top 20 documents)
4. Document Reranking (reorder by relevance)
    ↓ (keep top 5 documents)
5. LLM Generation (generate response with context)
    ↓
6. Cache Response (store for future queries)
    ↓
Final Response
```

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

### Query Examples

#### Basic Query
```python
response = rag_system.query("What is machine learning?")
```

#### Query with Custom Parameters
```python
response = rag_system.query(
    query="Explain neural networks",
    search_type="hybrid",
    alpha=0.6,
    retrieve_k=20,
    rerank_top_k=5,
    expand_query=True,
    use_cache=True
)
```

#### Disable Specific Features
```python
response = rag_system.query(
    query="What are transformers?",
    expand_query=False,  # Disable query expansion
    use_cache=False,     # Skip cache lookup
    search_type="semantic"  # Use only semantic search
)
```

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
alembic revision --autogenerate -m "Add semantic cache table"

# Create empty migration for manual changes
alembic revision -m "Add custom indexes for hybrid search"
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
- **Purpose**: Stores documents, chunks, metadata, and cache
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
- **Reranking**: Uses GPT-based relevance scoring

#### Cohere
- **Models**: Command, Command-light, Embed
- **Capabilities**: Text generation, embeddings, dedicated reranking
- **Configuration**: Requires COHERE_API_KEY
- **Use Cases**: Multilingual support, optimized reranking
- **Reranking**: Uses dedicated Rerank API (optimal performance)

### Vector Databases

#### Qdrant
- **Type**: Dedicated vector search engine
- **Deployment**: Cloud-hosted or self-hosted
- **Features**:
  - High-performance similarity search
  - Payload filtering
  - Real-time indexing
  - Horizontal scaling
  - Hybrid search support
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
  - Hybrid search with full-text search
- **Configuration**: Automatic with DATABASE_URL
- **Best For**: Smaller deployments, unified database architecture

## 🛠️ Configuration

### Environment Variables

All configuration is managed through environment variables in the `.env` file:

- **DATABASE_URL**: PostgreSQL connection string
- **LLM_PROVIDER**: Choice of LLM provider (openai, cohere)
- **VECTOR_DB**: Choice of vector database (qdrant, pgvector)
- **API Keys**: Provider-specific authentication
- **LOG_LEVEL**: Application logging verbosity
- **Search Features**: Enable/disable hybrid search, query expansion, cache, reranking
- **Search Parameters**: Alpha, expansion count, cache threshold, rerank top-k

### Provider Selection

Switch between providers by changing environment variables - no code changes required:

```bash
# Use OpenAI with Qdrant and all advanced features
LLM_PROVIDER=openai
VECTOR_DB=qdrant
ENABLE_HYBRID_SEARCH=true
ENABLE_QUERY_EXPANSION=true
ENABLE_SEMANTIC_CACHE=true
ENABLE_RERANKING=true

# Use Cohere with pgvector
LLM_PROVIDER=cohere
VECTOR_DB=pgvector
```

### Performance Tuning

```env
# Optimize for speed (lower quality)
HYBRID_SEARCH_ALPHA=0.8  # More keyword-based
QUERY_EXPANSION_COUNT=2  # Fewer variations
RERANK_TOP_K=5          # Rerank fewer documents

# Optimize for quality (slower)
HYBRID_SEARCH_ALPHA=0.3  # More semantic
QUERY_EXPANSION_COUNT=5  # More variations
RERANK_TOP_K=15         # Rerank more documents
```

## 📊 Logging

The application includes comprehensive logging:

- **File**: Detailed logs written to log files
- **Console**: Colored console output for development
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Configuration**: Managed through `logger.py`
- **Search Metrics**: Logs cache hits, search times, reranking scores

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/test_hybrid_search.py

# Run tests with verbose output
pytest -v

# Test specific features
pytest tests/test_query_expansion.py
pytest tests/test_semantic_cache.py
pytest tests/test_reranker.py
```

## 🙏 Acknowledgments

- **OpenAI**: GPT models and embeddings API
- **Cohere**: Language models, embedding services, and Rerank API
- **Qdrant**: High-performance vector search engine
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Rank-BM25**: Efficient BM25 implementation for keyword search

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
- Implement rate limiting for production deployments
- Monitor cache for sensitive information

---

**MiniRAG** - Advanced RAG system with hybrid search, query expansion, semantic caching, and document reranking