import argparse
import glob
import io
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

# Try best-effort PDF extractors. Prefer PyMuPDF for quality.
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except Exception:
    HAS_FITZ = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except Exception:
    HAS_PYPDF = False

# Optional token counting (graceful fallback)
try:
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text: str) -> int:
        return len(enc.encode(text))
except Exception:
    def count_tokens(text: str) -> int:
        # crude fallback ~4 chars per token
        return max(1, len(text) // 4)


@dataclass
class Chunk:
    doc_name: str
    index: int
    text: str
    pages: Tuple[int, int]
    n_tokens: int


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    # Convert Windows line endings, collapse weird spaces
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub("\xa0", " ", text)
    return text


def dehyphenate(text: str) -> str:
    # Join words split across line breaks: e.g., "hyphen-\nation" -> "hyphenation"
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    return text


def remove_page_numbers(line: str) -> bool:
    return bool(re.fullmatch(r"(?i)(page\s*)?\d+\s*(of\s*\d+)?", line.strip()))


def extract_with_pymupdf(file_bytes: bytes) -> List[Tuple[int, str]]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc, start=1):
        # use blocks to better preserve reading order
        text = page.get_text("text")
        pages.append((i, text or ""))
    return pages


def extract_with_pypdf(file_bytes: bytes) -> List[Tuple[int, str]]:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for i, p in enumerate(reader.pages, start=1):
        try:
            text = p.extract_text() or ""
        except Exception:
            text = ""
        pages.append((i, text))
    return pages


def extract_pdf_pages(file_bytes: bytes) -> List[Tuple[int, str]]:
    if HAS_FITZ:
        return extract_with_pymupdf(file_bytes)
    elif HAS_PYPDF:
        return extract_with_pypdf(file_bytes)
    else:
        raise RuntimeError("No PDF extractor available. Install PyMuPDF (pip install pymupdf) or pypdf.")


def strip_headers_footers(pages: List[Tuple[int, str]], threshold: float = 0.6) -> List[Tuple[int, str]]:
    """
    Heuristic: find short lines (<=120 chars) that repeat on >= threshold of pages and remove them.
    Helps remove headers, footers, and running titles.
    """
    line_occurs: Counter = Counter()
    page_lines: List[List[str]] = []
    for _, text in pages:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        page_lines.append(lines)
        for l in lines:
            if len(l) <= 120 and not remove_page_numbers(l):
                line_occurs[l] += 1

    n_pages = max(1, len(pages))
    repeated = {l for l, c in line_occurs.items() if c / n_pages >= threshold}

    cleaned_pages = []
    for (i, _), lines in zip(pages, page_lines):
        kept = []
        for l in lines:
            if l in repeated:
                continue
            if remove_page_numbers(l):
                continue
            kept.append(l)
        cleaned_pages.append((i, "\n".join(kept)))

    return cleaned_pages


def basic_clean(text: str) -> str:
    text = normalize(text)
    text = dehyphenate(text)
    # Collapse 3+ newlines to 2, and extra spaces
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def chunk_text(text: str, target_tokens: int = 1000, overlap_tokens: int = 100) -> List[str]:
    """Simple token-aware chunker that tries to break on paragraph boundaries."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    cur: List[str] = []
    cur_tok = 0

    for p in paragraphs:
        ptoks = count_tokens(p)
        if ptoks > target_tokens * 1.5:
            # very large paragraph; split by sentences as a fallback
            sentences = re.split(r"(?<=[.!?])[\s\n]+", p)
            for s in sentences:
                stoks = count_tokens(s)
                if cur_tok + stoks > target_tokens and cur:
                    chunks.append("\n\n".join(cur).strip())
                    # start next window with minimal overlap (last chunk tail)
                    if overlap_tokens > 0 and chunks[-1]:
                        tail = chunks[-1].split()[-overlap_tokens:]
                        cur = [" ".join(tail)]
                        cur_tok = count_tokens(cur[0])
                    else:
                        cur, cur_tok = [], 0
                cur.append(s)
                cur_tok += stoks
            continue

        if cur_tok + ptoks > target_tokens and cur:
            chunks.append("\n\n".join(cur).strip())
            if overlap_tokens > 0 and chunks[-1]:
                tail = chunks[-1].split()[-overlap_tokens:]
                cur = [" ".join(tail)]
                cur_tok = count_tokens(cur[0])
            else:
                cur, cur_tok = [], 0
        cur.append(p)
        cur_tok += ptoks

    if cur:
        chunks.append("\n\n".join(cur).strip())

    # final cleanup
    chunks = [c for c in chunks if c and len(c.split()) >= 5]
    return chunks


def dedupe_chunks(chunks: List[Chunk], min_jaccard: float = 0.9) -> List[Chunk]:
    """Very simple near-duplicate removal using Jaccard similarity on word sets."""
    kept: List[Chunk] = []
    signatures: List[set] = []
    for ch in chunks:
        ws = set(w.lower() for w in re.findall(r"\w+", ch.text))
        is_dup = False
        for sig in signatures:
            inter = len(ws & sig)
            union = max(1, len(ws | sig))
            if inter / union >= min_jaccard:
                is_dup = True
                break
        if not is_dup:
            kept.append(ch)
            signatures.append(ws)
    return kept


def build_dataset_from_pdfs(file_paths: List[str], target_tokens: int, overlap_tokens: int, rm_headers: bool, do_dedupe: bool):
    chunks: List[Chunk] = []

    for fp in file_paths:
        with open(fp, 'rb') as f:
            file_bytes = f.read()
        pages = extract_pdf_pages(file_bytes)
        if rm_headers:
            pages = strip_headers_footers(pages)
        page_texts = []
        for pno, ptxt in pages:
            cleaned = basic_clean(ptxt)
            page_texts.append((pno, cleaned))
        full_text = "\n\n".join(t for _, t in page_texts if t)
        # Chunk at document level but keep rough page bounds for audit
        doc_chunks = chunk_text(full_text, target_tokens=target_tokens, overlap_tokens=overlap_tokens)

        # Map chunk to page span by best-effort greedy allocation
        # (approximate; good enough for audit)
        cum_pages = []
        for pno, t in page_texts:
            cum_pages.append((pno, len(t)))
        total_chars = sum(c for _, c in cum_pages) or 1
        char_to_page = []
        running = 0
        for pno, clen in cum_pages:
            char_to_page.append((running, running + clen, pno))
            running += clen

        offset = 0
        for idx, text in enumerate(doc_chunks):
            # find page span by character offsets
            span_start = offset
            span_end = offset + len(text)
            offset = span_end
            pages_covered = [p for s, e, p in char_to_page if not (e <= span_start or s >= span_end)]
            if pages_covered:
                pmin, pmax = min(pages_covered), max(pages_covered)
            else:
                pmin = pmax = 1
            chunks.append(Chunk(
                doc_name=os.path.basename(fp),
                index=len(chunks),
                text=text,
                pages=(pmin, pmax),
                n_tokens=count_tokens(text),
            ))

    if do_dedupe:
        chunks = dedupe_chunks(chunks)

    # Build outputs
    jsonl_lines = []
    audit_lines = ["chunk_id,doc_name,page_start,page_end,approx_tokens"]
    total_tokens = 0

    for ch in chunks:
        record = {"text": ch.text}
        jsonl_lines.append(json.dumps(record, ensure_ascii=False))
        total_tokens += ch.n_tokens
        audit_lines.append(f"{ch.index},{ch.doc_name},{ch.pages[0]},{ch.pages[1]},{ch.n_tokens}")

    stats = {
        "num_documents": len(file_paths),
        "num_chunks": len(chunks),
        "total_approx_tokens": total_tokens,
        "avg_tokens_per_chunk": (total_tokens // max(1, len(chunks))) if chunks else 0,
    }
    return jsonl_lines, audit_lines, stats


def main():
    parser = argparse.ArgumentParser(description="Build CPT dataset from PDFs (CLI version)")
    parser.add_argument("input_dir", nargs='?', help="Directory containing PDF files (optional if --input_file is used)")
    parser.add_argument("--input_file", help="Path to a single PDF file")
    parser.add_argument("--output_jsonl", default="dataset.jsonl", help="Output JSONL file")
    parser.add_argument("--output_csv", default="audit.csv", help="Output audit CSV file")
    parser.add_argument("--target_tokens", type=int, default=1200, help="Target tokens per chunk")
    parser.add_argument("--overlap_tokens", type=int, default=80, help="Overlap tokens between chunks")
    parser.add_argument("--no_rm_headers", action="store_true", help="Do not remove repeated headers/footers")
    parser.add_argument("--no_dedupe", action="store_true", help="Do not perform near-duplicate removal")

    args = parser.parse_args()

    if args.input_file:
        if not os.path.isfile(args.input_file):
            print(f"File not found: {args.input_file}")
            return
        pdf_files = [args.input_file]
    elif args.input_dir:
        pdf_files = glob.glob(os.path.join(args.input_dir, "*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {args.input_dir}")
            return
    else:
        print("Either input_dir or --input_file must be provided")
        return

    rm_headers = not args.no_rm_headers
    do_dedupe = not args.no_dedupe

    print(f"Processing {len(pdf_files)} PDF(s)...")
    jsonl_lines, audit_lines, stats = build_dataset_from_pdfs(
        pdf_files, args.target_tokens, args.overlap_tokens, rm_headers, do_dedupe
    )

    with open(args.output_jsonl, 'w', encoding='utf-8') as f:
        for line in jsonl_lines:
            f.write(line + '\n')

    with open(args.output_csv, 'w', encoding='utf-8') as f:
        for line in audit_lines:
            f.write(line + '\n')

    print("Results:")
    print(f"  Documents: {stats['num_documents']}")
    print(f"  Chunks: {stats['num_chunks']}")
    print(f"  Total ~Tokens: {stats['total_approx_tokens']}")
    print(f"  Avg Tokens/Chunk: {stats['avg_tokens_per_chunk']}")
    print(f"Outputs: {args.output_jsonl}, {args.output_csv}")


if __name__ == "__main__":
    main()