"""Retrieve Hindi source chunks, generate a grounded answer, and cite metadata."""
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K, OLLAMA_URL, OLLAMA_MODEL

_model = None
_collection = None


def get_resources():
    global _model, _collection
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            _collection = client.get_collection(COLLECTION_NAME)
        except Exception as exc:
            raise RuntimeError("Vector index not found. Run `python src/extract_pdf.py` and `python src/index_documents.py` first.") from exc
    return _model, _collection


def retrieve(query: str, top_k: int = TOP_K):
    model, collection = get_resources()
    query_embedding = model.encode(["query: " + query], normalize_embeddings=True).tolist()[0]
    result = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, collection.count()), include=["documents", "metadatas", "distances"])
    sources = []
    for doc, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        score = max(0.0, min(1.0, 1.0 - float(distance) / 2.0))
        sources.append({"text": doc, **metadata, "score": score})
    return sources


def build_context(sources):
    return "\n\n".join(f"[SOURCE page={s['page']} section={s['section']!r} chunk_id={s['chunk_id']}]\n{s['text']}" for s in sources)


def generate_with_ollama(query: str, sources):
    prompt = f"""You are a careful question-answering assistant for a Hindi source document about A. P. J. Abdul Kalam.
Answer the user's question using ONLY the source context below.
- The source is mainly Hindi. Understand Hindi passages even when the question is in English.
- Answer in the same language as the question.
- If the context does not contain enough evidence, say that the provided document does not clearly state the answer.
- Do not invent facts, dates, or citations.
- Keep the answer concise.
- Do not write citations yourself; the application adds citations from retrieved metadata.

QUESTION:
{query}

SOURCE CONTEXT:
{build_context(sources)}

ANSWER:"""
    response = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=180)
    response.raise_for_status()
    answer = response.json().get("response", "").strip()
    if not answer:
        raise RuntimeError("Ollama returned an empty answer.")
    return answer


def extractive_fallback(query: str, sources):
    if not sources:
        return "पर्याप्त साक्ष्य नहीं मिला। / The retrieved context does not provide enough evidence."
    return "LOCAL LLM unavailable — showing the highest-ranked source passage instead of a generated answer.\nRetrieved passage: " + sources[0]["text"].strip()[:1200]


def answer_query(query: str, top_k: int = TOP_K, use_ollama: bool = True):
    sources = retrieve(query, top_k=top_k)
    if not sources:
        return {"query": query, "answer": "No relevant source chunks were retrieved.", "sources": []}
    if use_ollama:
        try:
            answer, mode = generate_with_ollama(query, sources), f"Ollama ({OLLAMA_MODEL})"
        except (requests.RequestException, RuntimeError, ValueError) as exc:
            answer, mode = extractive_fallback(query, sources), f"Extractive fallback ({type(exc).__name__})"
    else:
        answer, mode = extractive_fallback(query, sources), "Extractive fallback (LLM disabled)"
    return {"query": query, "answer": answer, "sources": sources, "mode": mode}


def format_result(result):
    lines = [f"### Question: {result['query']}", "", result["answer"], "", "**Automatic source citations:**"]
    if not result["sources"]:
        lines.append("- No sources retrieved.")
    else:
        for source in result["sources"]:
            lines.append(f"- page: {source['page']} · section: `{source['section']}` · chunk_id: `{source['chunk_id']}` · score: {source['score']:.3f}")
    lines += ["", f"_Answer mode: {result.get('mode', 'unknown')}_", ""]
    return "\n".join(lines)
