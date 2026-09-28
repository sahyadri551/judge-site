"""Deterministic legal-document chunking for the retrieval pipeline.

Milestone 3 baseline:
- 600 whitespace tokens per chunk
- 100-token overlap
- metadata-preserving chunks
- source PDF text extraction when Milestone 2 did not persist text
""" 

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable

_WORD_RE = re.compile(r"\S+")


@dataclass(frozen=True)
class ChunkingConfig:
    chunk_size: int = 600
    overlap: int = 100

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.overlap < 0:
            raise ValueError("overlap must be non-negative")
        if self.overlap >= self.chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")


def _tokens(text: str) -> list[str]:
    return _WORD_RE.findall(text)


def chunk_text(text: str, config: ChunkingConfig) -> list[tuple[str, int]]:
    """Split text into deterministic overlapping whitespace-token windows."""
    tokens = _tokens(text.strip())
    if not tokens:
        return []

    step = config.chunk_size - config.overlap
    chunks: list[tuple[str, int]] = []

    for start in range(0, len(tokens), step):
        window = tokens[start : start + config.chunk_size]
        if not window:
            break
        chunks.append((" ".join(window), len(window)))
        if start + config.chunk_size >= len(tokens):
            break

    return chunks


def chunk_document(
    document: dict[str, Any],
    text: str,
    config: ChunkingConfig | None = None,
) -> list[dict[str, Any]]:
    """Create chunks and propagate source metadata without inventing fields."""
    config = config or ChunkingConfig()
    doc_id = str(document["doc_id"])
    chunks = chunk_text(text, config)

    result: list[dict[str, Any]] = []
    for index, (chunk_text_value, token_count) in enumerate(chunks):
        result.append(
            {
                "chunk_id": f"{doc_id}:chunk:{index:05d}",
                "doc_id": doc_id,
                "doc_type": document.get("doc_type"),
                "pair_id": document.get("pair_id"),
                "source_pdf": document.get("source_pdf"),
                "caption_path": document.get("caption_path"),
                "caption_text": document.get("caption_text"),
                "pdf_filename": document.get("pdf_filename"),
                "chunk_index": index,
                "text": chunk_text_value,
                "token_count": token_count,
            }
        )

    return result
