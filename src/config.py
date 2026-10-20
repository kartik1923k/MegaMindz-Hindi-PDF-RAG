from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT_DIR / "data" / "Agni_Ki_Udaan_Adhyayan_Sahayika_Hindi.pdf"
OUTPUT_DIR = ROOT_DIR / "outputs"
PAGES_PATH = OUTPUT_DIR / "extracted_pages.jsonl"
CHUNKS_PATH = OUTPUT_DIR / "chunks.jsonl"
RESULTS_PATH = OUTPUT_DIR / "six_query_results.md"
CHROMA_DIR = ROOT_DIR / "chroma_db"
COLLECTION_NAME = "agni_ki_udaan_hindi"
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
TOP_K = 4
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"
