# Semantic RAG & Vector Search — Senior Gen AI Assessment

A local Retrieval-Augmented Generation (RAG) pipeline demonstrating semantic search with two retrieval strategies benchmarked against each other. Built to simulate a GCP/Vertex AI production architecture using free local tools.

---

## Table of Contents

1. [Setup and Running](#setup-and-running)
2. [Architecture Overview](#architecture-overview)
3. [Similarity Metric Choice](#similarity-metric-choice-cosine-vs-euclidean)
4. [Production Migration to Vertex AI](#production-migration-to-vertex-ai-vector-search)
5. [Test Suite](#test-suite)

---

## Setup and Running

### Prerequisites
- Python 3.10+
- Conda environment (recommended)
- Free Gemini API key from https://aistudio.google.com

### Installation

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd rag-assessment
```

**2. Activate your environment**
```bash
conda activate langchain_env
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
ENV=benchmark
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K=3
```

> ⚠️ Never commit `.env` to version control. It is listed in `.gitignore`.

**5. Run the benchmark**
```bash
python benchmark.py
```

This will:
- Ingest all 10 corpus chunks and embed them into FAISS
- Run 5 benchmark queries through both Strategy A and Strategy B
- Write outputs to `outputs/benchmark.json` and `outputs/retrieval_benchmark.md`

**6. Run tests**
```bash
python -m pytest tests/ -v
```

For coverage:
```bash
python -m pytest tests/ -v --cov=src
```

All 21 tests pass. GCP SDK calls are fully mocked — no API calls are made during testing.

---

## Architecture Overview

```
rag-assessment/
│
├── src/
│   ├── embeddings.py          # Local embedding model, mirrors Vertex AI interface
│   ├── vector_store.py        # FAISS-backed vector storage and similarity search
│   ├── query_expander.py      # LLM query expansion via Gemini API
│   ├── pipeline.py            # Central orchestrator — ingestion + retrieval strategies
│   └── benchmark.py           # Runs comparisons, generates JSON and Markdown reports
│
├── data/
│   └── corpus.py              # Knowledge base — 10 technical paragraphs + metadata
│
├── tests/
│   ├── conftest.py            # Shared pytest fixtures, mocks GCP SDK
│   ├── test_embeddings.py     # Embedding wrapper unit tests
│   ├── test_vector_store.py   # FAISS storage and search tests
│   ├── test_query_expander.py # LLM expansion tests with mocked model
│   └── test_pipeline.py       # End-to-end pipeline tests
│
├── outputs/
│   ├── benchmark.json              # Full structured results
│   └── retrieval_benchmark.md      # Human-readable comparison tables
│
├── benchmark.py               # Entry point
├── requirements.txt
└── .env                       # API key (never commit)
```

### Module Responsibilities

**`data/corpus.py`**

The knowledge base consists of 10 hand-crafted technical paragraphs covering load balancing, autoscaling, caching, database replication, API gateway, rate limiting, circuit breakers, message queues, monitoring/observability, and disaster recovery.

Paragraphs are deliberately written using varied vocabulary across related topics. For example, the load balancing paragraph uses "request distribution" and "round-robin" while the autoscaling paragraph uses "horizontal scaling" and "compute provisioning" — both relate to handling peak load but share zero overlapping terms. This forces the query expander to make a measurable difference in retrieval results.

**`src/embeddings.py`**

Wraps `sentence-transformers` (model: `all-MiniLM-L6-v2`) behind an interface that mirrors `vertexai.language_models.TextEmbeddingModel` exactly:

- `TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")` — same classmethod signature as Vertex AI, maps model name internally
- `get_embeddings(texts: list)` — returns a list of `EmbeddingResult` objects where each has a `.values` attribute containing a numpy array, exactly like Vertex AI
- `embed_single(text: str)` — convenience method returning a flat numpy array

Swapping this class for the real Vertex AI class in production requires zero changes to any other module.

**`src/vector_store.py`**

Manages the FAISS index with two supported similarity metrics:
- `cosine` — uses `IndexFlatIP` with L2-normalized vectors
- `euclidean` — uses `IndexFlatL2`

FAISS only stores vectors, not the original text. This class maintains a parallel Python list of chunk texts and metadata in insertion order, so index position in FAISS maps directly to position in those lists. Search results are returned as dicts containing `rank`, `chunk_text`, `score`, `metadata`, and `chunk_id`.

**`src/query_expander.py`**

Wraps any LLM client that implements `.generate_content(prompt)`. The model is injected via the constructor rather than instantiated internally — this is the key design decision that makes the class trivially mockable in tests without patching at the module level.

`create_gemini_expander(api_key)` is a factory function that wires up the real Gemini client and returns a ready `QueryExpander`. The import lives inside this function (not at module level) so test files can import `QueryExpander` without needing GCP credentials configured.

**`src/pipeline.py`**

The central orchestrator. All three dependencies (embedding model, vector store, query expander) are injected via constructor — nothing is created internally.

- `ingest(corpus_metadata)` — embeds each chunk and stores in FAISS, sets `_is_ingested` flag
- `retrieve_strategy_a(query, top_k)` — raw query → embed → FAISS search
- `retrieve_strategy_b(query, top_k)` — query → LLM expand → embed expanded query → FAISS search. Raises `ValueError` if no expander was provided.
- `compare(query, top_k)` — runs both strategies and computes overlap and unique chunk sets between the two result lists

**`src/benchmark.py`**

Runs all 5 benchmark queries through `pipeline.compare()`, collects results, and generates two output files. The Markdown report shows Strategy A vs Strategy B results side by side per query with similarity scores and a summary overlap table.

---

## Similarity Metric Choice: Cosine vs Euclidean

This pipeline uses **cosine similarity**.

### What each metric measures

**Euclidean distance** measures the straight-line distance between two points in vector space. It is sensitive to the magnitude (length) of vectors.

**Cosine similarity** measures the angle between two vectors. It is completely insensitive to magnitude — only direction matters.

### Why this matters for text

When a sentence is embedded, its vector magnitude is influenced by factors like sentence length and token frequency. Two sentences that express the same meaning but differ in length will produce vectors with different magnitudes but very similar directions.

Example: *"The system scales horizontally"* and *"The system automatically provisions additional compute instances to scale horizontally under load"* are semantically near-identical. Euclidean distance would penalize the second sentence for its larger magnitude, ranking it as less similar even though it conveys the same concept. Cosine similarity correctly identifies them as close because their vectors point in nearly the same direction.

### FAISS implementation detail

FAISS does not have a native cosine similarity index. The correct approach is to use `IndexFlatIP` (inner product) combined with L2-normalizing all vectors before insertion and before querying. When two unit vectors are compared via inner product, the result is mathematically identical to their cosine similarity. This approach is also faster than computing cosine directly because normalization happens once at insert time and search reduces to a simple dot product.

---

## Production Migration to Vertex AI Vector Search

The local architecture was designed from the start to mirror Vertex AI interfaces. Migration is four targeted swaps with no changes required to `pipeline.py`, `benchmark.py`, or any test logic.

### Step 1 — Embeddings

Replace `TextEmbeddingModelWrapper` with the real Vertex AI class:

```python
# Before (local)
from src.embeddings import TextEmbeddingModelWrapper
model = TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")

# After (production)
from vertexai.language_models import TextEmbeddingModel
model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
```

The method signatures `from_pretrained()`, `get_embeddings()` and the `.values` attribute on results are identical. No other code changes required.

### Step 2 — Vector Store

Replace the FAISS index with Vertex AI Matching Engine:

```python
from google.cloud import aiplatform

# Create index
index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name="rag-index",
    dimensions=768,
    approximate_neighbors_count=10,
)

# Deploy to endpoint
endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name="rag-endpoint",
    public_endpoint_enabled=True,
)
endpoint.deploy_index(index=index, deployed_index_id="rag_deployed")

# Query
response = endpoint.find_neighbors(
    deployed_index_id="rag_deployed",
    queries=[query_embedding],
    num_neighbors=top_k,
)
```

Wrap this behind the same `search(query_embedding, top_k)` interface as the current `VectorStore` class and `pipeline.py` requires zero changes.

### Step 3 — Query Expander

Replace `create_gemini_expander` with Vertex AI's generative model directly:

```python
# Before (local via google-genai SDK)
from src.query_expander import create_gemini_expander
expander = create_gemini_expander(api_key=os.getenv("GEMINI_API_KEY"))

# After (production via Vertex AI)
import vertexai
from vertexai.generative_models import GenerativeModel
vertexai.init(project="your-project-id", location="us-central1")
model = GenerativeModel("gemini-pro")
expander = QueryExpander(model=model)
```

The `.generate_content(prompt)` interface is identical. `QueryExpander` itself requires no changes.

### Step 4 — Authentication

Replace `.env` API key management with GCP service account credentials:

```python
# Before
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# After
import google.auth
credentials, project = google.auth.default()
vertexai.init(project=project, credentials=credentials)
```

In a Cloud Run or GKE deployment, `google.auth.default()` automatically picks up the attached service account — no credentials file or environment variable needed.

---

## Test Suite

21 tests across 4 files, all passing. GCP SDK is fully mocked — no API calls are made during test runs.

| File | Tests | What it covers |
|---|---|---|
| `test_embeddings.py` | 5 | Wrapper interface, output shape, model name mapping |
| `test_vector_store.py` | 6 | Add, batch add, search, result structure, cosine ranking, reset |
| `test_query_expander.py` | 4 | Model call, return type, prompt injection, batch |
| `test_pipeline.py` | 6 | Ingest flag, chunk count, Strategy A, Strategy B, no-expander error, compare keys |

The `conftest.py` fixtures inject fake embeddings (fixed `np.full((384,), 0.1)` arrays) and a mocked expander returning a hardcoded expanded query string. This means tests verify pipeline logic in complete isolation from any real model or API.