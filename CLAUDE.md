# CLAUDE.md

Briefing for Claude Code. Read this before doing anything in this repo.

## Who I am and how to work with me

I'm a CS student (Northeastern) building this project to learn cloud fundamentals and to prepare for internship interviews (Geode, Aera). I know Python basics and C, but I'm new to cloud, APIs, and RAG. Interviewers will ask me to explain every design choice, so **understanding matters more than speed.**

- **Teach, don't just do.** For concepts, guide me with leading questions and small hints before giving the answer. For code I'm learning, let me write it first, then review it.
- **Small steps.** One change at a time. Show what changed and explain it line by line, especially anything new (syntax, libraries, AWS services).
- **Concrete examples work best for me.** Tiny test data (like chunking `"ABCDEFGHIJKLMNOP"`) helps more than abstract explanations.
- **Connect each step to cloud concepts** (IAM, Regions, managed services, cost, idempotency) and to how I'd explain it in an interview.
- **Ask before big changes** (new files, refactors, new dependencies, anything that touches AWS or costs money).
- If you write a larger piece of plumbing code for me, explain it afterwards and check that I understand it.

## Project goal

A document Q&A assistant (RAG): upload PDFs, ask questions, get answers that cite the source document and page. Built in three stages.

**Week 1, local (in progress):** extract PDF text, chunk with file/page metadata, embed and store in Chroma, FastAPI `POST /ask` that retrieves top chunks, sends them to an LLM, and returns an answer with citations. pytest tests for chunking and retrieval.

**Week 2, AWS:** PDFs in S3; upload triggers a Lambda that runs ingestion. Amazon Bedrock for embeddings and the LLM (like Geode's "LLM Gateway"). Vectors in Postgres + pgvector on RDS. API in Docker on App Runner (or Lambda + API Gateway). IAM roles with minimal permissions; secrets in Secrets Manager, never in code.

**Week 3, professional:** GitHub Actions for tests and deploy (CI/CD). Evaluation script with ~20 test questions measuring hit rate at k across chunk sizes (e.g. 400 / 800 / 1200), with recorded numbers. Architecture diagram and README.

**Optional:** CSVs in S3 queried with Athena + Glue (for Aera).

## Current state

Files:
- `app/ingest.py`: `extract_pages(pdf_path)` returns `[{source, page, text}]` with 1-based pages. `chunk_pages(pages, chunk_size, overlap)` cleans whitespace with `" ".join(text.split())`, skips pages under 100 cleaned characters, and slices with `step = chunk_size - overlap`. Each chunk: `{source, page, chunk_size, chunk_index, text}`.
- `app/store.py`: Chroma `PersistentClient` at `chroma_db/`, collection `lab_reports`. `build_index(chunks)` upserts with IDs `"{source}-p{page}-c{chunk_index}"`. `search(question, k)` returns hits with text, distance, and metadata. The `__main__` block indexes my lab report PDF.
- `app/api.py`: FastAPI `POST /search` with a pydantic `Question` model (`question: str`, `k: int = 3`), plus `GET /` health check.
- `experiments/embedding_similarity.py`: cosine similarity demo (similar meaning ≈ 0.50, unrelated ≈ 0.08).

Run locally:
- Index: `python -m app.store`
- API: `uvicorn app.api:app --reload`, test page at http://127.0.0.1:8000/docs

**Next steps, in order:**
1. Test `k = -1` and `k = 100000` on `/search`, then add `Field(3, ge=1, le=10)` range validation.
2. Build `POST /ask`: retrieve top chunks, prompt an LLM, return an answer with source + page citations. LLM provider not chosen yet. Discuss options with me first.
3. pytest tests for `chunk_pages` (fake pages) and retrieval.

## Design decisions so far (I should be able to explain these)

- **Chunk size 800, overlap 150.** At 160 chars, an explanation got cut before the key sentence; one complete idea in my reports is a few hundred characters. Overlap keeps boundary sentences whole in a neighbor chunk. To be tuned with measured results in Week 3. Note: pages average ~780 chars, so many pages become one chunk.
- **Top k = 3.** Embeddings match topic better than intent. For "How is signed overflow detected?", the top hit was a test-results table (page 15), while the actual rule was on page 14 and page 11.
- **Chroma returns distance (lower = closer)**, not similarity. Default is squared L2; similarity ≈ 1 − distance / 2.
- **Upsert + unique IDs = idempotent ingestion**, important because Lambda may retry.
- **Validation:** pydantic rejects bad types with 422; range limits also protect cost once Bedrock is involved.

## Known limitations and data notes

- Tables stored as images aren't extracted by pypdf (e.g. pages 57–58 of my portfolio). Planned upgrade: Bedrock vision model in Week 2.
- Ligature artifacts: "tt" → `+`, "ti" → `9`, `ﬁ`/`ﬂ` characters, subscript 2 → `ଶ`. `unicodedata.normalize("NFKC", ...)` fixes some.
- Fixed-size chunks can start mid-word.
- Cover pages (~200 chars) contain my student ID. Don't expose them in demos.

## Rules

- **Never commit** `data/`, `chroma_db/`, `.venv/`, `.DS_Store`, or any credentials. My PDFs are private.
- No secrets in code or in cloud environment variables. Use Secrets Manager (Week 2).
- **Cost:** AWS account is on the Free plan ($100 credits, Region `us-east-2`). Budget alert at $10. Avoid OpenSearch Serverless (charges when idle). Stop RDS when not working. Estimate cost before using paid services.
- Use one AWS Region for everything and confirm Bedrock model availability there first.
- Keep `requirements.txt` updated with `pip freeze > requirements.txt` after installing packages.
- Keep the README Status checklist current.

## Cloud sessions note

In Claude Code cloud sessions, `data/` and `chroma_db/` don't exist (git-ignored) and network access is limited, so Chroma can't download its embedding model. Use fake data for tests there; run real indexing and search on my Mac.
