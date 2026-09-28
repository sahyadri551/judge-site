from backend.ingestion.chunking import ChunkingConfig, chunk_document, chunk_text


def test_short_document_produces_one_chunk_and_preserves_metadata() -> None:
    document = {
        "doc_id": "judgment:1",
        "doc_type": "judgment",
        "pair_id": 1,
        "source_pdf": "data/raw/example.pdf",
        "caption_path": "data/raw/metadata1.txt",
        "caption_text": "Example caption",
        "pdf_filename": "1.pdf",
    }

    chunks = chunk_document(document, "one two three four five", ChunkingConfig(10, 2))

    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "judgment:1:chunk:00000"
    assert chunks[0]["doc_id"] == "judgment:1"
    assert chunks[0]["doc_type"] == "judgment"
    assert chunks[0]["pair_id"] == 1
    assert chunks[0]["caption_text"] == "Example caption"
    assert chunks[0]["token_count"] == 5


def test_overlap_repeats_expected_tokens() -> None:
    chunks = chunk_text(
        " ".join(f"token{i}" for i in range(12)),
        ChunkingConfig(chunk_size=6, overlap=2),
    )

    assert [text for text, _ in chunks] == [
        "token0 token1 token2 token3 token4 token5",
        "token4 token5 token6 token7 token8 token9",
        "token8 token9 token10 token11",
    ]


def test_empty_document_produces_no_chunks() -> None:
    assert chunk_document({"doc_id": "empty"}, "   ") == []


def test_invalid_chunk_configuration() -> None:
    for config in ((0, 0), (100, 100), (100, -1)):
        try:
            ChunkingConfig(*config)
        except ValueError:
            continue
        raise AssertionError(f"Expected invalid configuration: {config}")
