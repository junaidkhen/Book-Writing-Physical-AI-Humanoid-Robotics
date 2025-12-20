# Quickstart Guide: Retrieval Pipeline Validation

**Feature**: 001-retrieval-pipeline-validation
**Date**: 2025-12-16
**Purpose**: Step-by-step guide to execute validation and interpret results

## Prerequisites

Before running the retrieval validation, ensure these conditions are met:

### 1. Environment Setup
- **Python Version**: Python 3.11+ (tested with 3.12.3)
- **Dependencies Installed**: Run `pip install -r requirements.txt`
- **Environment Variables**: Configure `.env` file with:
  ```bash
  QDRANT_URL=https://your-qdrant-instance.cloud.qdrant.io:6333
  QDRANT_API_KEY=your_qdrant_api_key
  COHERE_API_KEY=your_cohere_api_key
  ```

### 2. Qdrant Collection Populated
- **Prerequisite**: Document ingestion (Spec-1/002-document-ingestion-core) must be completed first
- **Verify collection exists**:
  ```bash
  python3 -c "
  from qdrant_client import QdrantClient
  from dotenv import load_dotenv
  import os

  load_dotenv()
  client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))

  collection = client.get_collection('documents')
  print(f'✓ Collection: {collection.name}')
  print(f'✓ Vector count: {collection.points_count}')
  print(f'✓ Vector size: {collection.config.params.vectors.size}')
  print(f'✓ Distance metric: {collection.config.params.vectors.distance}')
  "
  ```
- **Expected Output**:
  ```
  ✓ Collection: documents
  ✓ Vector count: 537
  ✓ Vector size: 1024
  ✓ Distance metric: Cosine
  ```
- **If collection does not exist**: Run document ingestion first:
  ```bash
  python3 main.py  # Runs ingestion pipeline (Spec-1)
  ```

---

## Quick Start: Run Validation

### Option 1: Default Configuration (Recommended)

```bash
python3 main.py --validate-retrieval
```

**What this does**:
- Loads 20 test queries from `validation/spec2/test_queries.json`
- Retrieves top-10 results per query from Qdrant
- Measures latency, relevance, ranking quality
- Performs 5% integrity check on Qdrant collection
- Generates validation report in `validation/spec2/report.md`
- Writes raw results to `validation/spec2/results.json`

**Expected Duration**: 30-60 seconds (depending on Qdrant/Cohere API latency)

---

### Option 2: Custom Configuration

```bash
python3 main.py --validate-retrieval --top-k 20 --output /path/to/custom/report.md
```

**Parameters**:
- `--top-k K`: Retrieve top-K results per query (default: 10)
- `--output PATH`: Custom path for validation report (default: validation/spec2/report.md)

**Example**:
```bash
python3 main.py --validate-retrieval --top-k 5 --output ~/validation-2025-12-16.md
```

---

## Interpreting Results

### Step 1: Check Exit Code

```bash
python3 main.py --validate-retrieval
echo "Exit code: $?"
```

**Exit Codes**:
- `0`: Validation successful, all success criteria met ✅
- `1`: Validation completed with warnings, some success criteria not met ⚠️
- `2`: Fatal error (Qdrant unavailable, missing collection, API key invalid) ❌

---

### Step 2: Read Validation Report

Open `validation/spec2/report.md` (or custom output path) in a Markdown viewer or text editor.

**Report Structure**:
```markdown
# Retrieval Pipeline Validation Report

## Executive Summary
- ✅ SC-001: Query Success Rate (100%)
- ✅ SC-002: Metadata Completeness (100%)
- ✅ SC-003: Monotonic Score Decrease (95% pass)
- ❌ SC-004: Average Latency (612ms, target: <500ms)
...

## Performance Metrics
- Average Latency: 612ms
- P50 Latency: 480ms
- P95 Latency: 890ms
...

## Quality Metrics
- Average Similarity Score: 0.74
- Score Distribution:
  - High (≥0.78): 85 chunks
  - Medium (0.60-0.78): 45 chunks
  - Low (0.40-0.60): 10 chunks
  - Incorrect (<0.40): 0 chunks
...

## Integrity Metrics
- Total Vectors: 537
- Valid Payload %: 100%
- Missing URLs: 0
- Missing Text: 0
...
```

---

### Step 3: Review Success Criteria

| ID | Criterion | Target | Actual | Status |
|----|-----------|--------|--------|--------|
| SC-001 | Query success rate | 100% | 100% | ✅ |
| SC-002 | Metadata completeness | 100% | 100% | ✅ |
| SC-003 | Monotonic score decrease | ≥90% | 95% | ✅ |
| SC-004 | Average latency | <500ms | 612ms | ❌ |
| SC-005 | Zero integrity issues | 0 issues | 0 issues | ✅ |
| SC-006 | Top-3 relevance | ≥80% | *Manual* | ⏸️ |
| SC-007 | No system errors | 0 errors | 0 errors | ✅ |
| SC-008 | Schema validation | Pass | Pass | ✅ |

**Status Legend**:
- ✅ **Pass**: Criterion met
- ❌ **Fail**: Criterion not met, requires investigation
- ⏸️ **Manual**: Requires human validation (see Step 4)

---

### Step 4: Manual Validation for SC-006

**Purpose**: Verify that 80% of queries return semantically relevant results in top-3 positions.

**Process**:
1. Open `validation/spec2/results.json`
2. For each query, review the top-3 `retrieved_chunks`
3. Ask: "Do these chunks help answer the query?"
4. Count queries where ≥1 of top-3 chunks are relevant
5. Calculate: (relevant_queries / total_queries) × 100

**Example**:
```json
{
  "query_id": 1,
  "query_text": "What is physical AI?",
  "retrieved_chunks": [
    {
      "score": 0.87,
      "text": "Physical AI refers to artificial intelligence systems that interact with the physical world...",
      "relevance_label": "High"
    },
    {
      "score": 0.79,
      "text": "Embodied intelligence enables robots to perceive and manipulate objects...",
      "relevance_label": "High"
    },
    {
      "score": 0.72,
      "text": "Humanoid robotics combines AI with mechanical engineering...",
      "relevance_label": "Medium"
    }
  ]
}
```

**Judgment**: ✅ **Relevant** (top-3 all discuss physical AI concepts)

**After completing manual validation**:
- Update report.md with: `SC-006: ✅ Pass (85% of queries have relevant top-3)`
- If <80% relevant, mark as: `SC-006: ❌ Fail (72% relevant, requires chunking/embedding tuning)`

---

## Troubleshooting

### Problem: "Qdrant collection 'documents' not found"

**Cause**: Document ingestion (Spec-1) has not been run yet

**Solution**:
```bash
# Run document ingestion first
python3 main.py

# Wait for completion (may take 5-30 minutes depending on corpus size)
# Then run validation
python3 main.py --validate-retrieval
```

---

### Problem: "Cohere API rate limit exceeded"

**Cause**: Too many API calls in short time (20 queries × 1 embedding each = 20 calls)

**Solution**:
- Wait 60 seconds and retry
- Check Cohere dashboard for rate limit details
- Upgrade Cohere plan if frequently hitting limits

**Mitigation**: Code already includes exponential backoff retry logic

---

### Problem: "Average latency >500ms (SC-004 fails)"

**Cause**: Qdrant query latency or Cohere embedding latency too high

**Investigation**:
1. Check report.md for latency breakdown:
   - If P50 <500ms but P95 >500ms → outliers, acceptable
   - If P50 >500ms → systemic issue

2. Identify bottleneck:
   ```bash
   # Check Qdrant latency (should be <100ms)
   time python3 -c "
   from qdrant_client import QdrantClient
   from dotenv import load_dotenv
   import os
   load_dotenv()
   client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))
   client.query_points('documents', query=[0.1]*1024, limit=10)
   "

   # Check Cohere latency (should be <200ms)
   time python3 -c "
   import cohere
   from dotenv import load_dotenv
   import os
   load_dotenv()
   co = cohere.Client(api_key=os.getenv('COHERE_API_KEY'))
   co.embed(texts=['test query'], model='embed-english-v3.0')
   "
   ```

3. **Mitigations**:
   - **Qdrant slow**: Upgrade Qdrant cluster tier, enable caching
   - **Cohere slow**: Check network latency to Cohere API, consider regional endpoints
   - **Acceptable**: If P95 <1000ms, latency is within reasonable bounds for non-production validation

---

### Problem: "Monotonic decrease pass rate <90% (SC-003 fails)"

**Cause**: Retrieved chunks not properly ranked by similarity

**Investigation**:
1. Open results.json and find queries with non-monotonic scores:
   ```json
   "retrieved_chunks": [
     {"score": 0.85},
     {"score": 0.72},
     {"score": 0.78},  // ❌ Violates monotonic decrease (0.72 → 0.78)
     {"score": 0.65}
   ]
   ```

2. **Possible Causes**:
   - Qdrant bug (unlikely)
   - Incorrect distance metric (should be Cosine)
   - Corrupted embeddings during ingestion

3. **Mitigation**:
   - Verify Qdrant collection schema: `distance_metric = Cosine`
   - Re-run ingestion if schema incorrect
   - Check Qdrant client version (should be ≥1.6.0)

---

### Problem: "Top-3 relevance rate <80% (SC-006 fails manual validation)"

**Cause**: Retrieved chunks not semantically relevant to queries

**Investigation**:
1. Review low-relevance queries in results.json
2. Common patterns:
   - Broad queries ("robot") → generic chunks
   - Out-of-domain queries ("quantum computers") → no good matches
   - Technical jargon mismatches → embedding model limitation

3. **Mitigations**:
   - **Chunking**: Adjust chunk size (current: ~500 tokens) → larger chunks for better context
   - **Embedding Model**: Experiment with different Cohere models (e.g., embed-multilingual if corpus is non-English)
   - **Query Expansion**: Add synonyms or rephrase queries
   - **Re-labeling**: Review if relevance thresholds (High ≥0.78) are too strict for corpus

**Action**: Document findings in report.md and iterate on Spec-1 ingestion parameters

---

## Next Steps After Validation

### If All Success Criteria Pass ✅

1. **Archive Validation Report**:
   ```bash
   cp validation/spec2/report.md validation/spec2/report-$(date +%Y%m%d).md
   ```

2. **Proceed to Next Spec**:
   - Spec-3: RAG Agent implementation (LLM-based answer generation)
   - Spec-4: FastAPI + Docusaurus integration (user-facing chatbot)

3. **Set Up Monitoring** (optional):
   - Run validation weekly to detect retrieval quality regressions
   - Track latency trends over time
   - Compare score distributions across validation runs

---

### If Any Success Criteria Fail ❌

1. **Prioritize Failures**:
   - **Critical**: SC-001 (no results), SC-002 (missing metadata), SC-007 (system errors)
   - **High**: SC-003 (ranking broken), SC-006 (low relevance)
   - **Medium**: SC-004 (latency), SC-005 (integrity issues)
   - **Low**: SC-008 (schema validation, should never fail)

2. **Iterate on Ingestion** (if SC-002, SC-003, SC-005, SC-006 fail):
   - Adjust chunking parameters (size, overlap)
   - Verify embedding model consistency
   - Check data source quality (broken URLs, malformed content)
   - Re-run Spec-1 ingestion with updated parameters

3. **Infrastructure Optimization** (if SC-004 fails):
   - Upgrade Qdrant cluster
   - Optimize network latency
   - Consider Cohere API regional endpoints

4. **Re-run Validation** after fixes:
   ```bash
   python3 main.py --validate-retrieval --output validation/spec2/report-iteration2.md
   ```

5. **Document Iterations**:
   - Keep all validation reports: `report-iteration1.md`, `report-iteration2.md`, etc.
   - Track what changed between iterations
   - Record final working configuration in plan.md

---

## Advanced: Batch Validation

To run validation multiple times (e.g., for A/B testing different chunking strategies):

```bash
#!/bin/bash
# batch-validation.sh

# Iteration 1: Baseline (default parameters)
python3 main.py --validate-retrieval --output validation/spec2/baseline-report.md

# Iteration 2: Larger chunks (modify main.py CHUNK_SIZE)
sed -i 's/CHUNK_SIZE = 500/CHUNK_SIZE = 1000/' main.py
python3 main.py  # Re-run ingestion
python3 main.py --validate-retrieval --output validation/spec2/large-chunks-report.md

# Iteration 3: Different embedding model (modify main.py COHERE_MODEL)
sed -i 's/embed-english-v3.0/embed-english-light-v3.0/' main.py
python3 main.py  # Re-run ingestion
python3 main.py --validate-retrieval --output validation/spec2/light-model-report.md

# Compare results
diff validation/spec2/baseline-report.md validation/spec2/large-chunks-report.md
diff validation/spec2/baseline-report.md validation/spec2/light-model-report.md
```

---

## FAQ

**Q: How long does validation take?**
A: Typically 30-60 seconds for 20 queries (depends on API latency)

**Q: Can I add more test queries?**
A: Yes, edit `validation/spec2/test_queries.json` and add entries following the schema

**Q: Can I run validation without Qdrant Cloud (local Qdrant)?**
A: Yes, change `QDRANT_URL` in `.env` to `http://localhost:6333` and remove `QDRANT_API_KEY`

**Q: What if I want to test different k values?**
A: Use `--top-k` flag: `python3 main.py --validate-retrieval --top-k 20`

**Q: How do I automate validation in CI/CD?**
A: Run validation in GitHub Actions and fail build if exit code ≠ 0:
```yaml
- name: Run Retrieval Validation
  run: python3 main.py --validate-retrieval

- name: Check Success Criteria
  run: |
    if grep -q "❌" validation/spec2/report.md; then
      echo "Validation failed"
      exit 1
    fi
```

---

## Support & References

- **Feature Spec**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Validation Report Schema**: [contracts/validation-report-schema.json](./contracts/validation-report-schema.json)
- **Test Queries**: `validation/spec2/test_queries.json`
- **Implementation**: `main.py` lines 351-647
