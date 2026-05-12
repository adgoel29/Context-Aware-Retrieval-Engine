import os
from dotenv import load_dotenv

from data.corpus import CORPUS_METADATA
from src.embeddings import TextEmbeddingModelWrapper
from src.vector_store import VectorStore
from src.query_expander import create_gemini_expander
from src.pipeline import RAGPipeline
from src.benchmark import BenchmarkRunner, BENCHMARK_QUERIES

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not set in .env")

# --- Wire up components ---
embedding_model = TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")
vector_store = VectorStore(similarity_metric="cosine")
query_expander = create_gemini_expander(api_key=GEMINI_API_KEY)

pipeline = RAGPipeline(
    embedding_model=embedding_model,
    vector_store=vector_store,
    query_expander=query_expander,
)

# --- Ingest corpus ---
print("Ingesting corpus...")
result = pipeline.ingest(CORPUS_METADATA)
print(f"  {result['chunks_ingested']} chunks ingested | dim={result['embedding_dim']} | {result['status']}")

# --- Run benchmark ---
runner = BenchmarkRunner(pipeline, output_dir="outputs/")
runner.generate_report(BENCHMARK_QUERIES)