# Quick Implementation Guide - Latency Optimization

## Overview
This guide provides step-by-step instructions to reduce complaint processing latency by 50-70%.

**Current Performance:**
- CSV/Excel/Narratives: 40-50 seconds
- PDFs: 60+ seconds

**Target Performance:**
- CSV/Excel/Narratives: 12-18 seconds (60-70% reduction)
- PDFs: 15-20 seconds (67-75% reduction)

---

## Phase 1: Quick Wins (Immediate - 50-60% Reduction)

### Step 1: Switch to Claude Haiku (5 minutes)

**File:** `src/app/extract_and_process_complaints/lambda_function.py`

**Change Line ~220:**
```python
# BEFORE:
modelId="anthropic.claude-3-5-sonnet-20240620-v1:0"

# AFTER:
modelId="anthropic.claude-3-haiku-20240307-v1:0"
```

**Expected Impact:** 3-5x faster LLM responses (30-40% total reduction)

---

### Step 2: Replace Prompts (10 minutes)

**Files to replace:**
1. `src/app/extract_and_process_complaints/prompt.txt`
2. `src/app/extract_and_process_complaints/prompt_narrative.txt`

**Actions:**
```bash
cd src/app/extract_and_process_complaints/

# Backup originals
copy prompt.txt prompt_original.txt
copy prompt_narrative.txt prompt_narrative_original.txt

# Replace with optimized versions
copy ..\..\..\OPTIMIZED_prompt.txt prompt.txt
copy ..\..\..\OPTIMIZED_prompt_narrative.txt prompt_narrative.txt
```

**Expected Impact:** 20-30% faster token processing

---

### Step 3: Add Parallel Processing (30 minutes)

**File:** `src/app/extract_and_process_complaints/lambda_function.py`

**Add import at top:**
```python
from concurrent.futures import ThreadPoolExecutor
```

**Replace lambda_handler function:**
```python
def lambda_handler(event, context):
    """Main Lambda handler with parallel processing"""
    try:
        logger.info("Complaint processing started")
        
        if 'Records' in event:
            # OPTIMIZED: Parallel batch processing
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(process_single_complaint, json.loads(record['body']))
                    for record in event['Records']
                ]
                results = [f.result() for f in futures]
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'processed_count': len(results),
                    'results': results
                })
            }
        else:
            # Direct invocation
            result = process_single_complaint(event)
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': str(e)})
        }
```

**Update SQS Configuration:**

**File:** `variables.tf` (or your tfvars file)

Find the extract_and_process_complaints lambda config and update SQS settings:
```hcl
sqs_trigger = [{
  queue_name         = "preload-complaints"
  visibility_timeout = 900
  max_receive_count  = 3
  batch_size         = 10        # CHANGED from 1 to 10
  max_batch_window   = 5         # CHANGED from 0 to 5
  max_concurrency    = 10        # ADD this line
}]
```

**Expected Impact:** 10x throughput when processing multiple complaints

---

### Deploy Phase 1

```bash
# Package lambda
cd src/app/extract_and_process_complaints
zip -r ../../../extract_and_process_complaints.zip .

# Deploy with Terraform
cd ../../..
terraform plan
terraform apply
```

**Test Phase 1:**
1. Upload a CSV with 10 complaints
2. Monitor CloudWatch logs for timing metrics
3. Verify all complaints processed correctly

**Expected Results After Phase 1:**
- CSV/Excel: 40-50s → 15-20s per complaint
- PDFs: 60s → 20-25s per complaint
- Batch of 10: ~20s total (instead of 400-500s)

---

## Phase 2: Additional Optimizations (1-2 days)

### Step 4: Add Connection Pooling (1 hour)

**File:** `src/app/extract_and_process_complaints/requirements.txt`

**Add:**
```
psycopg-pool>=3.2.0
```

**File:** `src/app/extract_and_process_complaints/lambda_function.py`

**Add import:**
```python
from psycopg_pool import ConnectionPool
```

**Add after imports:**
```python
_connection_pool = None

def get_connection_pool():
    """Get or create database connection pool"""
    global _connection_pool, _db_credentials
    
    if _connection_pool is not None:
        return _connection_pool
    
    try:
        _db_credentials = get_secret(DB_SECRET_NAME, DB_REGION)
        
        host = _db_credentials['host']
        port = _db_credentials.get('port', 5432)
        dbname = _db_credentials['dbname']
        user = _db_credentials['username']
        password = _db_credentials['password']
        
        conninfo = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        
        _connection_pool = ConnectionPool(
            conninfo,
            min_size=2,
            max_size=10,
            timeout=30
        )
        
        logger.info("Database connection pool created")
        return _connection_pool
        
    except Exception as e:
        logger.error(f"Error creating connection pool: {str(e)}")
        raise
```

**Update update_complaint_in_db function:**
```python
def update_complaint_in_db(complaint_id, extracted_data):
    """Update complaint record using connection pool"""
    try:
        pool = get_connection_pool()
        
        # Use connection pool
        with pool.connection() as conn:
            with conn.cursor() as cur:
                # ... rest of existing code
```

**Expected Impact:** 5-10% reduction in DB overhead

---

### Step 5: Optimize PDF Processing (1 hour)

**File:** `src/app/extract_and_process_complaints/lambda_function.py`

**Update pdf_to_images function:**
```python
def process_page(doc, page_num):
    """Process single PDF page"""
    page = doc[page_num]
    # Reduced resolution from 1.5 to 1.0
    pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    return img

def pdf_to_images(pdf_data):
    """Convert PDF pages to PIL Images with parallel processing"""
    doc = None
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        page_count = min(doc.page_count, MAX_PAGES)
        
        # Parallel page processing
        with ThreadPoolExecutor(max_workers=4) as executor:
            images = list(executor.map(lambda i: process_page(doc, i), range(page_count)))
        
        return images
    except Exception as e:
        logger.error(f"Error converting PDF: {str(e)}")
        raise
    finally:
        if doc:
            doc.close()
```

**Update images_to_base64 function:**
```python
def images_to_base64(images):
    """Convert PIL Images to base64 with compression"""
    base64_images = []
    for img in images:
        buffer = io.BytesIO()
        # Add compression
        img.save(buffer, format='PNG', optimize=True, quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf8')
        base64_images.append(img_base64)
    return base64_images
```

**Expected Impact:** 15-20% faster PDF processing

---

### Step 6: Add Performance Monitoring (30 minutes)

**File:** `src/app/extract_and_process_complaints/lambda_function.py`

**Update process_single_complaint function:**
```python
def process_single_complaint(message_data):
    """Process a single complaint with timing"""
    import time
    start_time = time.time()
    
    try:
        input_type = validate_event(message_data)
        complaint_id = message_data['complaint_id']
        
        logger.info(f"Processing complaint {complaint_id} ({input_type})")
        
        pdf_time = 0
        llm_time = 0
        
        if input_type == 'pdf':
            pdf_start = time.time()
            pdf_data = fetch_pdf_from_s3(message_data['s3path'])
            images = pdf_to_images(pdf_data)
            base64_images = images_to_base64(images)
            messages = construct_pdf_prompt(base64_images)
            pdf_time = time.time() - pdf_start
            
        elif input_type == 'narrative':
            messages = construct_narrative_prompt(message_data['narrative_text'])
        
        llm_start = time.time()
        extracted_data = process_with_bedrock(messages, input_type)
        llm_time = time.time() - llm_start
        
        db_start = time.time()
        update_complaint_in_db(complaint_id, extracted_data)
        db_time = time.time() - db_start
        
        total_time = time.time() - start_time
        
        logger.info(f"Complaint {complaint_id} timings - Total: {total_time:.2f}s, PDF: {pdf_time:.2f}s, LLM: {llm_time:.2f}s, DB: {db_time:.2f}s")
        
        return {
            'success': True,
            'complaint_id': complaint_id,
            'input_type': input_type,
            'timings': {
                'total': total_time,
                'pdf_processing': pdf_time,
                'llm_call': llm_time,
                'db_update': db_time
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing complaint: {str(e)}")
        raise
```

---

### Deploy Phase 2

```bash
# Package lambda with new dependencies
cd src/app/extract_and_process_complaints
pip install -r requirements.txt -t .
zip -r ../../../extract_and_process_complaints.zip .

# Deploy
cd ../../..
terraform apply
```

**Expected Results After Phase 2:**
- CSV/Excel: 15-20s → 12-15s per complaint
- PDFs: 20-25s → 15-18s per complaint

---

## Testing & Validation

### Test Suite

**1. Single Narrative Test:**
```bash
aws lambda invoke \
  --function-name qms-dev-extract-and-process-complaints \
  --payload file://test_narrative_event.json \
  response.json
```

**test_narrative_event.json:**
```json
{
  "complaint_id": "TEST001",
  "file_id": "test-file-001",
  "narrative_text": "Patient experienced severe headache after taking medication. Product lot number ABC123."
}
```

**2. PDF Test:**
```bash
aws lambda invoke \
  --function-name qms-dev-extract-and-process-complaints \
  --payload file://test_pdf_event.json \
  response.json
```

**3. Batch Test:**
Upload CSV with 10 complaints and monitor CloudWatch logs.

### Validation Checklist

- [ ] All required fields extracted correctly
- [ ] Narrative summary generated appropriately
- [ ] Processing time reduced by 50%+
- [ ] No errors in CloudWatch logs
- [ ] Database records updated correctly
- [ ] Parallel processing working (check logs for concurrent execution)

---

## Monitoring

### CloudWatch Metrics to Watch

1. **Lambda Duration**: Should decrease by 50-70%
2. **Lambda Concurrent Executions**: Should increase with parallel processing
3. **SQS Messages Processed**: Should process batches of 10
4. **Bedrock Invocations**: Should see Haiku model calls
5. **Database Connections**: Should see connection pooling

### CloudWatch Logs Insights Queries

**Average Processing Time:**
```
fields @timestamp, complaint_id, timings.total
| filter @message like /timings/
| stats avg(timings.total) as avg_time by input_type
```

**LLM Call Duration:**
```
fields @timestamp, complaint_id, timings.llm_call
| filter @message like /timings/
| stats avg(timings.llm_call) as avg_llm_time
```

---

## Rollback Plan

If issues occur, rollback is simple:

**1. Revert to Sonnet:**
```python
modelId="anthropic.claude-3-5-sonnet-20240620-v1:0"
```

**2. Restore Original Prompts:**
```bash
copy prompt_original.txt prompt.txt
copy prompt_narrative_original.txt prompt_narrative.txt
```

**3. Disable Parallel Processing:**
```python
# In lambda_handler, replace parallel processing with:
results = []
for record in event['Records']:
    result = process_single_complaint(json.loads(record['body']))
    results.append(result)
```

**4. Redeploy:**
```bash
terraform apply
```

---

## Cost Impact

### Before Optimization (Sonnet)
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- Average cost per complaint: ~$0.05

### After Optimization (Haiku)
- Input: $0.25 per 1M tokens (92% cheaper)
- Output: $1.25 per 1M tokens (92% cheaper)
- Average cost per complaint: ~$0.005

**Estimated Savings:** 90% reduction in LLM costs

---

## Success Metrics

### Target Metrics (After Full Implementation)

| Metric | Before | Target | Improvement |
|--------|--------|--------|-------------|
| CSV/Excel Processing | 40-50s | 12-18s | 60-70% |
| PDF Processing | 60s | 15-20s | 67-75% |
| Batch of 10 (CSV) | 400-500s | 15-20s | 95% |
| LLM Cost per Complaint | $0.05 | $0.005 | 90% |
| Throughput (complaints/min) | 1-2 | 30-40 | 20x |

---

## Troubleshooting

### Issue: Haiku accuracy lower than expected
**Solution:** 
- Test with 100 sample complaints
- Compare extraction accuracy
- If < 90%, revert to Sonnet with prompt caching

### Issue: Bedrock throttling errors
**Solution:**
- Reduce ThreadPoolExecutor max_workers from 10 to 5
- Reduce SQS batch_size from 10 to 5
- Request quota increase from AWS

### Issue: Database connection errors
**Solution:**
- Increase connection pool max_size
- Check Aurora Serverless scaling
- Verify VPC/security group settings

### Issue: Lambda timeout
**Solution:**
- Current timeout: 900s (15 min)
- Should be sufficient even for batches
- Check CloudWatch logs for specific bottleneck

---

## Next Steps

After successful implementation:

1. **Monitor for 1 week** - Collect performance metrics
2. **A/B Test** - Compare accuracy between Haiku and Sonnet
3. **Fine-tune** - Adjust batch sizes based on actual performance
4. **Document** - Update runbooks with new performance baselines
5. **Scale** - Consider increasing concurrent executions if needed

---

## Support

For issues or questions:
1. Check CloudWatch logs first
2. Review this guide's troubleshooting section
3. Test with single complaint before batch processing
4. Keep original files as backup for quick rollback
