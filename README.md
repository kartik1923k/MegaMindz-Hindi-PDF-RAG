# MegaMindz Hindi PDF RAG Assignment

A local-first retrieval-augmented generation (RAG) project for asking Hindi and English questions about the supplied Hindi study guide, **Agni Ki Udaan — A. P. J. Abdul Kalam**.

## Features

- Extracts text page-by-page from the supplied PDF with PyMuPDF.
- Normalizes Hindi text using Unicode NFC and cleans common spacing artifacts.
- Creates overlapping chunks and stores page, section heading, and unique chunk ID metadata.
- Embeds Hindi passages and English/Hindi questions with `intfloat/multilingual-e5-base`.
- Persists vectors in ChromaDB using cosine distance.
- Retrieves relevant Hindi passages for both Hindi and English queries.
- Uses a local Ollama model (`qwen2.5:3b`) to produce answers grounded in retrieved context.
- Automatically prints citations from retrieved metadata: page, section, chunk ID, and retrieval score.
- Runs all six required assignment questions and writes a Markdown report to `outputs/six_query_results.md`.

## Requirements

- Python 3.10 or 3.11 recommended.
- Internet access for first-time package and model downloads. The embedding model is free and runs locally after download.
- Optional Ollama installation for local answer generation. Without Ollama, the project displays the highest-ranked retrieved passage as a fallback and clearly labels it; this fallback is not an LLM-generated answer.

## Setup in VS Code (Windows PowerShell)

Open this project folder in VS Code, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this in the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

The supplied PDF is included in the ZIP at `data/Agni_Ki_Udaan_Adhyayan_Sahayika_Hindi.pdf`.

## Build and run

Run from the project root, in this order:

```powershell
python src/extract_pdf.py
python src/index_documents.py
```

For local answer generation, install Ollama, then run:

```powershell
ollama pull qwen2.5:3b
```

Keep Ollama running, then ask questions:

```powershell
python src/ask.py "कलाम को भारत रत्न किस वर्ष प्राप्त हुआ?"
python src/ask.py "Which institution did Kalam attend to study aeronautical engineering?"
```

Run all six required queries:

```powershell
python src/run_six_queries.py
```

The report is saved to `outputs/six_query_results.md`. It is generated on your computer; this ZIP does not pretend to contain pre-verified model answers.

To inspect retrieval without Ollama:

```powershell
python src/ask.py "पोखरण-II में कलाम की क्या भूमिका थी?" --no-llm
```

## Design choices

### Chunking strategy

Chunks target **900 characters** with **150 characters of overlap**. The extractor first respects blank-line paragraph boundaries and then sentence endings, including Hindi danda `।`; character windows are used only for unusually long text. Overlap helps retain context when a fact falls near a chunk boundary. These are practical starting values, not a claim that they are optimal.

### Embeddings and multilingual retrieval

`intfloat/multilingual-e5-base` is a multilingual embedding model. E5 inputs use the `passage: ` prefix for document chunks and `query: ` for questions. This is intended to let English questions retrieve semantically related Hindi passages; verify the six required queries rather than assuming retrieval is perfect.

### Vector database

ChromaDB was selected because it is open-source, straightforward to run locally, and supports persistent collections with metadata. Every vector stores `page`, `section`, and `chunk_id`, so citations are generated from retrieved records instead of being hardcoded into answer text.

### Answer generation and grounding

The default local generator is Ollama with `qwen2.5:3b`. The prompt instructs it to use only retrieved context and admit when evidence is missing. The application adds source citations from metadata after generation. Retrieval scores are display scores derived from cosine distance; they are **not calibrated probabilities**. A local LLM can still make mistakes, so check all six answers against the source PDF before submission.

### Hindi handling and tables

The PDF is extracted page-by-page as UTF-8 text and normalized with Unicode NFC. Chunking respects Hindi punctuation. Table content is preserved to the extent PyMuPDF exposes it in extracted text; this baseline does not reconstruct complex table cell geometry. Review extracted pages/chunks for the awards table and timeline. OCR is not included because the supplied PDF has selectable text.

## Troubleshooting

- **No vector index:** run extraction and indexing in order.
- **First run is slow:** the embedding model is downloaded once and may be several hundred MB.
- **Ollama connection error:** start Ollama and run `ollama pull qwen2.5:3b`, or use `--no-llm` to inspect retrieval.
- **Poor retrieval/citations:** inspect `outputs/chunks.jsonl` and compare retrieved chunks with the six required questions.
- **No extracted text:** the PDF may be image-only; OCR would be needed for such a source.

## Limitations and improvements

- The heading detector uses the first meaningful line on each page; a continuation page may receive a less useful section label.
- Table extraction is text-based and does not fully preserve cell structure.
- Answer quality depends on the embedding model and local LLM; the required questions need manual evaluation.
- Useful improvements include OCR/table extraction, retrieval metrics (Recall@k / MRR), reranking, and source-snippet highlighting.

## GitHub note

The source PDF is included in this ZIP for local convenience. `data/*.pdf` is excluded by `.gitignore` to avoid publicly redistributing the supplied document without checking its usage rights. If the assignment permits public redistribution, remove that ignore rule before committing; otherwise document how the evaluator can place the supplied PDF locally.

## Project structure

```text
MegaMindz_Hindi_PDF_RAG/
├── data/
│   └── Agni_Ki_Udaan_Adhyayan_Sahayika_Hindi.pdf
├── src/
│   ├── config.py
│   ├── extract_pdf.py
│   ├── index_documents.py
│   ├── rag.py
│   ├── ask.py
│   └── run_six_queries.py
├── outputs/
├── chroma_db/
├── requirements.txt
├── .gitignore
└── README.md
```
