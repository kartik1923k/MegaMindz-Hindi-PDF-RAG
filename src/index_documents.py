"""Embed extracted chunks and persist them in ChromaDB."""
import json
import chromadb
from sentence_transformers import SentenceTransformer
from config import CHUNKS_PATH, CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL


def main():
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError("Run first: python src/extract_pdf.py")
    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]
    if not chunks:
        raise RuntimeError("No chunks found. Check the PDF extraction output.")
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    print("First run downloads the open multilingual model; this may take time.")
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = ["passage: " + item["text"] for item in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True).tolist()
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine", "description": "Hindi PDF RAG assignment"})
    batch_size = 64
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        collection.add(
            ids=[x["chunk_id"] for x in batch],
            documents=[x["text"] for x in batch],
            metadatas=[{"page": int(x["page"]), "section": str(x["section"]), "chunk_id": str(x["chunk_id"])} for x in batch],
            embeddings=embeddings[start:start + batch_size],
        )
    print(f"Indexing completed. Chunks indexed: {collection.count()}\nPersistent database: {CHROMA_DIR}")

if __name__ == "__main__":
    main()
