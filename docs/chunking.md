# Milestone 3 — Legal Document Chunking

## Baseline

- 600 whitespace tokens per chunk
- 100-token overlap
- 500-token stride
- Output: `data/processed/chunks.jsonl`

The current corpus contract from Milestone 2 does not require extracted
text to be present in `documents.jsonl`. Therefore this milestone extracts
text from each source PDF when the record has no `text` field.

The raw PDFs are read only; they are never modified.

## Chunk record

Every chunk contains the Milestone 2 source metadata plus:

- `chunk_id`
- `chunk_index`
- `text`
- `token_count`

No case, party, citation, section, or other legal metadata is inferred.

## Reproducibility

The chunker is deterministic. Chunk size and overlap can be changed through
the CLI, so later experiments can compare variants without changing the
baseline implementation.

Example:

`python -m backend.ingestion --input data/processed/documents.jsonl --output data/processed/chunks.jsonl --project-root .`

## Research note

The baseline deliberately uses fixed windows. A later experiment should
compare this against structure-aware legal chunking (paragraph/section-aware
boundaries) and evaluate retrieval metrics. The baseline is an engineering
control, not a claim that 600/100 is optimal.
