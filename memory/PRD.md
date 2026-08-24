# NyayaAI Product Record

## Original problem statement
Develop an AI-powered Legal Research Assistant for Indian law that retrieves relevant judgments and legal provisions, then generates a cited answer using a Small Language Model. The initial brief names FastAPI, Streamlit, FAISS, BM25, embedding models, and quantized 3B–4B SLMs, with public Indian legal resources including Supreme Court judgments, the Constitution, BNS, BNSS, Consumer Protection, Motor Vehicles, and labour laws.

## Architecture decisions
- React frontend with FastAPI backend, using `REACT_APP_BACKEND_URL` for all browser API calls.
- Deterministic local demo engine for source-grounded synthesis; no external AI key required.
- Seeded in-memory corpus for the MVP, with clear citations and a legal disclaimer.
- Three app areas: Ask Nyaya, Source Library, and Corpus Health.

## User personas
- Indian law student or researcher checking a provision or precedent.
- Advocate or legal operations user needing a fast, source-visible starting point.
- Demo reviewer assessing grounded SLM research workflows.

## Core requirements (static)
- Ask a legal question and retrieve cited Indian-law sources.
- Show confidence, retrieval metrics, source detail, and verification disclaimer.
- Browse and filter statutes and landmark judgments.
- Show corpus and retrieval health.
- Work on desktop and mobile.

## Implemented
- 2026-08-24: Built NyayaAI Q&A workspace with suggested prompts, recent research, scoped search, deterministic grounded answer generation, confidence and retrieval metrics, citations, copy controls, and disclaimer.
- 2026-08-24: Added source library with search, category filtering, source detail modal, source copy, and query-from-source action.
- 2026-08-24: Added corpus health dashboard with indexed corpus statistics, distribution bars, and grounding architecture explanation.
- 2026-08-24: Fixed clipboard permission handling and stale category filter; verified desktop/mobile flows and API regressions.

## Prioritized backlog
- P0: Replace seeded corpus with an official-source ingestion pipeline and persistent index.
- P1: Add persistent saved research history and user workspaces.
- P1: Add document upload and quote-level source highlighting.
- P2: Add exportable research briefs and bilingual Hindi answers.

## Next tasks
1. Connect official Gazette and Supreme Court datasets.
2. Add persistent FAISS/BM25 indexes and scheduled refresh.
3. Add source snippets and amendment/version dates.
4. Evaluate a real quantized local SLM against citation-grounding benchmarks.
