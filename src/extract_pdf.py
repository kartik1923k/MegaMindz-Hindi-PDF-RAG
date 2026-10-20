"""Extract text page-by-page, normalize Hindi Unicode, and create cited chunks."""
import json
import re
import unicodedata
import fitz
from config import PDF_PATH, OUTPUT_DIR, PAGES_PATH, CHUNKS_PATH, CHUNK_SIZE, CHUNK_OVERLAP


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_section(text: str, page_number: int) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return f"पृष्ठ {page_number}"
    first = lines[0]
    if len(first) <= 140 and (re.match(r"^\d+\s*[·.)]", first) or "अब्दुल कलाम" in first or "विषय-सूची" in first):
        return first
    return first[:140]


def split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Prefer paragraph/sentence boundaries, including Hindi danda (।)."""
    if not text:
        return []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    units = []
    for paragraph in paragraphs:
        if len(paragraph) <= size:
            units.append(paragraph)
        else:
            sentences = re.split(r"(?<=[।.!?])\s+", paragraph)
            current = ""
            for sentence in sentences:
                if current and len(current) + len(sentence) + 1 > size:
                    units.append(current.strip())
                    current = sentence
                else:
                    current = f"{current} {sentence}".strip()
            if current:
                units.append(current.strip())
    chunks, current = [], ""
    for unit in units:
        if len(unit) > size:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(unit):
                chunks.append(unit[start:start + size].strip())
                if start + size >= len(unit):
                    break
                start += size - overlap
            continue
        candidate = f"{current}\n{unit}".strip() if current else unit
        if len(candidate) <= size:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            tail = current[-overlap:] if current and overlap else ""
            current = f"{tail}\n{unit}".strip() if tail else unit
            if len(current) > size:
                current = current[-size:]
    if current:
        chunks.append(current.strip())
    result = []
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk and (not result or chunk != result[-1]):
            result.append(chunk)
    return result


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Source PDF not found: {PDF_PATH}\nPlace the supplied Hindi PDF in the data folder with the expected filename.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    page_records, chunk_records = [], []
    with fitz.open(PDF_PATH) as doc:
        for page_index, page in enumerate(doc):
            page_number = page_index + 1
            text = normalize_text(page.get_text("text"))
            section = detect_section(text, page_number)
            page_records.append({"page": page_number, "section": section, "text": text})
            for local_index, chunk_text in enumerate(split_text(text)):
                chunk_records.append({"chunk_id": f"p{page_number:02d}_c{local_index:03d}", "page": page_number, "section": section, "text": chunk_text})
    with PAGES_PATH.open("w", encoding="utf-8") as f:
        for item in page_records:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    with CHUNKS_PATH.open("w", encoding="utf-8") as f:
        for item in chunk_records:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    chars = sum(len(p["text"]) for p in page_records)
    print("PDF extraction completed.")
    print(f"Pages: {len(page_records)}\nExtracted characters: {chars}\nChunks: {len(chunk_records)}")
    print(f"Pages file: {PAGES_PATH}\nChunks file: {CHUNKS_PATH}")
    if chars == 0:
        raise RuntimeError("No selectable text was extracted. This PDF may need OCR.")

if __name__ == "__main__":
    main()
