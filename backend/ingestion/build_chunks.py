"""Build chunks.jsonl from Milestone 2 documents.jsonl."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from pypdf import PdfReader

from .chunking import ChunkingConfig, chunk_document


def _read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Expected JSON object on line {line_number} of {path}")
            yield record


def extract_pdf_text(source_pdf: str | Path, project_root: Path) -> str:
    """Extract text from a source PDF while leaving the raw PDF untouched."""
    pdf_path = Path(source_pdf)
    if not pdf_path.is_absolute():
        pdf_path = project_root / pdf_path

    if not pdf_path.exists():
        raise FileNotFoundError(f"Source PDF does not exist: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.replace("\x00", " ").strip()
        if text:
            pages.append(text)

    return "\n\n".join(pages)


def build_chunks(
    input_path: str | Path = "data/processed/documents.jsonl",
    output_path: str | Path = "data/processed/chunks.jsonl",
    project_root: str | Path = ".",
    config: ChunkingConfig | None = None,
) -> dict[str, Any]:
    """Build the complete chunk corpus and return deterministic run statistics."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    project_root = Path(project_root)
    if not input_path.is_absolute():
        input_path = project_root / input_path
    if not output_path.is_absolute():
        output_path = project_root / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    config = config or ChunkingConfig()

    total_documents = 0
    total_chunks = 0
    zero_chunk_documents: list[str] = []
    total_tokens = 0
    min_tokens: int | None = None
    max_tokens: int | None = None

    with output_path.open("w", encoding="utf-8", newline="\n") as out:
        for document in _read_jsonl(input_path):
            total_documents += 1
            text = str(document.get("text") or "").strip()
            if not text:
                text = extract_pdf_text(str(document["source_pdf"]), project_root)

            chunks = chunk_document(document, text, config)
            if not chunks:
                zero_chunk_documents.append(str(document.get("doc_id")))
                continue

            for chunk in chunks:
                out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                count = int(chunk["token_count"])
                total_chunks += 1
                total_tokens += count
                min_tokens = count if min_tokens is None else min(min_tokens, count)
                max_tokens = count if max_tokens is None else max(max_tokens, count)

    return {
        "input": str(input_path),
        "output": str(output_path),
        "chunk_size": config.chunk_size,
        "overlap": config.overlap,
        "total_documents": total_documents,
        "total_chunks": total_chunks,
        "zero_chunk_documents": zero_chunk_documents,
        "min_chunk_tokens": min_tokens or 0,
        "max_chunk_tokens": max_tokens or 0,
        "average_chunk_tokens": round(total_tokens / total_chunks, 2) if total_chunks else 0.0,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/processed/documents.jsonl")
    parser.add_argument("--output", default="data/processed/chunks.jsonl")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--chunk-size", type=int, default=600)
    parser.add_argument("--overlap", type=int, default=100)
    args = parser.parse_args()

    summary = build_chunks(
        input_path=args.input,
        output_path=args.output,
        project_root=args.project_root,
        config=ChunkingConfig(args.chunk_size, args.overlap),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
