# Latency Optimization Analysis - Extract & Process Complaints

## Current Architecture Analysis

### Flow Overview
1. **create_complaint** → Creates complaint record → Sends to SQS
2. **upload_complaints** → Parses file (CSV/Excel/PDF) → Creates records → Sends to SQS
3. **extract_and_process_complaints** → Processes from SQS → Calls Bedrock LLM → Updates DB

### Current Performance
- **CSV/Excel/Manual Narratives**: 40-50 seconds
- **PDFs**: 60+ seconds

### Bottleneck Identification

#### Primary Bottleneck: LLM Processing
The `extract_and_process_complaints` lambda makes a **single synchronous Bedrock API call** that:
- For PDFs: Processes multiple images + 5KB prompt
- For narratives: Processes 3KB prompt + narrative text
- Uses Claude 3.5 Sonnet with tool calling
- Waits for complete response before proceeding

#### Secondary Bottlenecks
1. **PDF Processing**: Converting PDF to images (fitz library)
2. **Sequential Processing**: One complaint at a time from SQS
3. **Prompt Size**: Very large prompts (5KB for PDF, 3KB for narrative)
4. **Database Updates**: Single transaction per complaint

---

## Optimization Strategies to Reduce Latency by 50%+

### 🚀 Strategy 1: Parallel Batch Processing (HIGHEST IMPACT)
**Expected Reduction: 40-60%**

#### Current State
- SQS batch size: Configured per lambda
- Processing: Sequential (one at a time)

#### Optimization
```python
def lambda_handler(event, context):
    if 'Records' in event:
        # Process ALL records in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_single_complaint, json.loads(record['body'])) 
                      for record in event['Records']]
            results = [f.result() for f in futures]
```

#### Implementation
- Increase SQS batch size to 10
- Use Python ThreadPoolExecutor for parallel Bedrock calls
- Bedrock supports high concurrency

**Impact**: Process 10 complaints in ~45s instead of 450s

---

### 🚀 Strategy 2: Prompt Optimization (HIGH IMPACT)
**Expected Reduction: 20-30%**

#### Current Issues
- **prompt.txt**: 5,000+ characters with repetitive instructions
- **prompt_narrative.txt**: 3,000+ characters
- Excessive examples and redundant definitions

#### Optimization
**Reduce prompt size by 60-70%** while maintaining accuracy:

```
BEFORE: 5KB prompt with examples, definitions, repeated instructions
AFTER: 1.5KB focused prompt with essential instructions only
```

**Key Changes**:
1. Remove duplicate field definitions
2. Consolidate AE/PC classification into 2 sentences
3. Remove verbose examples (keep 1-2 critical ones)
4. Use bullet points instead of paragraphs
5. Remove redundant "Document Specific Instructions"

**Impact**: Faster token processing = 20-30% latency reduction

---

### 🚀 Strategy 3: Use Faster Bedrock Model (MEDIUM-HIGH IMPACT)
**Expected Reduction: 30-40%**

#### Current Model
- `anthropic.claude-3-5-sonnet-20240620-v1:0`
- High accuracy, slower speed

#### Optimization Options

**Option A: Claude 3 Haiku (Recommended)**
```python
modelId="anthropic.claude-3-haiku-20240307-v1:0"
```
- **3-5x faster** than Sonnet
- 70-80% of Sonnet's accuracy (sufficient for structured extraction)
- **Cost**: 90% cheaper

**Option B: Claude 3.5 Sonnet with Prompt Caching**
```python
response = bedrock_runtime.converse(
    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
    messages=messages,
    toolConfig={...},
    system=[{
        "text": prompt_text,
        "cacheControl": {"type": "ephemeral"}
    }]
)
```
- Cache the large prompt instructions
- 90% cost reduction on cached tokens
- 50% latency reduction on subsequent calls

**Recommendation**: Start with Haiku for 3-5x speedup

---

### 🚀 Strategy 4: Optimize PDF Processing (MEDIUM IMPACT - PDFs only)
**Expected Reduction: 15-20% for PDFs**

#### Current Implementation
```python
pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # High resolution
```

#### Optimization
```python
# Reduce resolution for faster processing
pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))  # 33% smaller images

# Compress images before base64 encoding
img.save(buffer, format='PNG', optimize=True, quality=85)

# Process pages in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    images = list(executor.map(process_page, range(page_count)))
```

**Impact**: 15-20% faster PDF processing

---

### 🚀 Strategy 5: Database Connection Pooling (LOW-MEDIUM IMPACT)
**Expected Reduction: 5-10%**

#### Current Implementation
- Creates new connection per complaint
- Connection cached at module level (good)

#### Optimization
```python
from psycopg_pool import ConnectionPool

# Initialize pool once (outside handler)
_connection_pool = None

def get_connection_pool():
    global _connection_pool
    if _connection_pool is None:
        conninfo = get_connection_string()
        _connection_pool = ConnectionPool(
            conninfo,
            min_size=2,
            max_size=10,
            timeout=30
        )
    return _connection_pool

def update_complaint_in_db(complaint_id, extracted_data):
    pool = get_connection_pool()
    with pool.connection() as conn:
        # Use pooled connection
```

**Impact**: 5-10% reduction in DB overhead

---

### 🚀 Strategy 6: Async Database Updates (MEDIUM IMPACT)
**Expected Reduction: 10-15%**

#### Optimization
Don't wait for DB update to complete - fire and forget:

```python
def process_single_complaint(message_data):
    # Extract data from LLM
    extracted_data = process_with_bedrock(messages, spec_type)
    
    # Queue DB update asynchronously (don't wait)
    executor.submit(update_complaint_in_db, complaint_id, extracted_data)
    
    return {'success': True, 'complaint_id': complaint_id}
```

**Impact**: 10-15% faster by not blocking on DB writes

---

### 🚀 Strategy 7: Reduce Tool Spec Complexity (LOW-MEDIUM IMPACT)
**Expected Reduction: 5-10%**

#### Current toolspec.json
- 12 fields with nested objects
- Verbose descriptions

#### Optimization
```json
{
  "toolSpec": {
    "name": "extract_case_info",
    "description": "Extract case info from complaint docs",
    "inputSchema": {
      "json": {
        "type": "object",
        "properties": {
          "case_id": {"type": "string"},
          "receipt_date": {"type": "string"},
          "criticality": {"type": "string"},
          "category": {"type": "array", "items": {"type": "string"}},
          "case_type": {"type": "array", "items": {"type": "string"}},
          "narrative": {"type": "string"},
          "narrative_summary": {"type": "string"},
          "primary_reporter": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "address": {"type": "string"}
            }
          },
          "product_details": {
            "type": "object",
            "properties": {
              "drug_name": {"type": "string"},
              "dosage": {"type": "string"},
              "lot_no": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

Remove verbose descriptions - they're already in the prompt.

---

## Implementation Priority & Expected Results

### Phase 1: Quick Wins (1-2 days) - 50-60% Reduction
1. ✅ **Switch to Claude Haiku** (30-40% reduction)
2. ✅ **Optimize prompts** (20-30% reduction)
3. ✅ **Parallel batch processing** (40-60% reduction when processing multiple)

**Expected Result**: 
- CSV/Excel: 40-50s → **15-20s**
- PDFs: 60s → **20-25s**

### Phase 2: Additional Optimizations (3-5 days) - Additional 15-20%
4. ✅ **PDF processing optimization** (15-20% for PDFs)
5. ✅ **Connection pooling** (5-10%)
6. ✅ **Async DB updates** (10-15%)

**Expected Result**:
- CSV/Excel: 15-20s → **12-15s**
- PDFs: 20-25s → **15-18s**

### Phase 3: Advanced (Optional) - Additional 10-15%
7. ✅ **Prompt caching** (if staying with Sonnet)
8. ✅ **Tool spec simplification** (5-10%)

---

## Recommended Implementation Plan

### Step 1: Model Switch (Immediate - No Code Changes)
```python
# In extract_and_process_complaints/lambda_function.py
# Line ~220 in process_with_bedrock()

# CHANGE FROM:
modelId="anthropic.claude-3-5-sonnet-20240620-v1:0"

# CHANGE TO:
modelId="anthropic.claude-3-haiku-20240307-v1:0"
```

### Step 2: Prompt Optimization (1 day)
- Reduce prompt.txt from 5KB to 1.5KB
- Reduce prompt_narrative.txt from 3KB to 1KB
- Test accuracy with sample complaints

### Step 3: Parallel Processing (1 day)
- Add ThreadPoolExecutor to lambda_handler
- Increase SQS batch size to 10
- Test with multiple complaints

### Step 4: PDF Optimization (1 day)
- Reduce image resolution
- Add image compression
- Parallel page processing

### Step 5: Database Optimizations (1-2 days)
- Implement connection pooling
- Make DB updates async
- Test under load

---

## Testing Strategy

### Performance Testing
```python
# Add timing to lambda_handler
import time

def process_single_complaint(message_data):
    start = time.time()
    
    # Existing code...
    
    timings = {
        'total': time.time() - start,
        'pdf_processing': pdf_time,
        'llm_call': llm_time,
        'db_update': db_time
    }
    logger.info(f"Timings: {timings}")
```

### A/B Testing
1. Deploy optimized version to separate lambda
2. Route 10% of traffic to new version
3. Compare latency metrics
4. Gradually increase traffic

---

## Risk Mitigation

### Model Switch Risk
- **Risk**: Lower accuracy with Haiku
- **Mitigation**: 
  - Test on 100 sample complaints
  - Compare extraction accuracy
  - Keep Sonnet as fallback for complex cases

### Parallel Processing Risk
- **Risk**: Bedrock rate limits
- **Mitigation**:
  - Start with batch size of 5
  - Monitor throttling errors
  - Implement exponential backoff

### Prompt Optimization Risk
- **Risk**: Missing critical information
- **Mitigation**:
  - A/B test with original prompts
  - Validate all required fields extracted
  - Keep original prompts as backup

---

## Cost Impact

### Current Cost (Sonnet)
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

### With Haiku
- Input: $0.25 per 1M tokens (92% cheaper)
- Output: $1.25 per 1M tokens (92% cheaper)

**Estimated Savings**: 90%+ on LLM costs while being 3-5x faster

---

## Monitoring & Metrics

### Key Metrics to Track
```python
# CloudWatch metrics
- complaint_processing_duration_ms
- llm_call_duration_ms
- pdf_processing_duration_ms
- db_update_duration_ms
- extraction_accuracy_rate
- bedrock_throttle_errors
```

### Alerts
- Processing time > 30s (warning)
- Processing time > 60s (critical)
- Extraction accuracy < 95%
- Bedrock throttle rate > 5%

---

## Summary

**Target**: Reduce latency by 50%+

**Recommended Approach**:
1. Switch to Claude Haiku → **3-5x faster**
2. Optimize prompts → **20-30% faster**
3. Parallel processing → **10x throughput**
4. PDF optimizations → **15-20% faster for PDFs**

**Expected Final Results**:
- CSV/Excel: 40-50s → **12-18s** (60-70% reduction) ✅
- PDFs: 60s → **15-20s** (67-75% reduction) ✅

**Implementation Time**: 3-5 days for all optimizations
**Risk Level**: Low (all changes are reversible)
**Cost Impact**: 90% reduction in LLM costs
