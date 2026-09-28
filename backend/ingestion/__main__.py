from .build_chunks import build_chunks
from .chunking import ChunkingConfig

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Build legal chunks from documents.jsonl")
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
