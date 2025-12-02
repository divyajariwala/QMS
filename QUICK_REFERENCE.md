# Quick Reference Card - Latency Optimization

## 🎯 Goal
Reduce complaint processing time from 40-60s to 12-18s (60-75% reduction)

---

## 📊 Current vs Target Performance

| Type | Current | Target | Improvement |
|------|---------|--------|-------------|
| CSV/Excel | 45s | 15s | 67% |
| PDF | 60s | 18s | 70% |
| Batch of 10 | 450s | 20s | 96% |

---

## 🚀 Top 3 Optimizations (Fastest Impact)

### 1. Switch to Claude Haiku (5 min) - 30-40% reduction
```python
# File: src/app/extract_and_process_complaints/lambda_function.py
# Line: ~220

# CHANGE FROM:
modelId="anthropic.claude-3-5-sonnet-20240620-v1:0"

# CHANGE TO:
modelId="anthropic.claude-3-haiku-20240307-v1:0"
```

### 2. Replace Prompts (10 min) - 20-30% reduction
```bash
cd src/app/extract_and_process_complaints/
copy ..\..\..\OPTIMIZED_prompt.txt prompt.txt
copy ..\..\..\OPTIMIZED_prompt_narrative.txt prompt_narrative.txt
```

### 3. Enable Parallel Processing (30 min) - 10x throughput
```python
# Add to lambda_handler in lambda_function.py
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_single_complaint, json.loads(r['body'])) 
               for r in event['Records']]
    results = [f.result() for f in futures]
```

**Update SQS batch size to 10 in variables.tf**

---

## 📁 Files to Modify

| File | Change | Impact |
|------|--------|--------|
| `lambda_function.py` | Model ID + Parallel processing | 50-60% |
| `prompt.txt` | Replace with optimized | 20-30% |
| `prompt_narrative.txt` | Replace with optimized | 20-30% |
| `variables.tf` | SQS batch_size = 10 | 10x throughput |
| `requirements.txt` | Add psycopg-pool | 5-10% |

---

## 🔧 Quick Deploy

```bash
# 1. Make changes to files above
# 2. Package lambda
cd src/app/extract_and_process_complaints
zip -r ../../../extract_and_process_complaints.zip .

# 3. Deploy
cd ../../..
terraform apply
```

---

## 📈 Expected Results

### After 1 Hour (Phase 1)
- CSV: 45s → 15s ✅
- PDF: 60s → 20s ✅
- Cost: 90% reduction ✅

### After 1-2 Days (Phase 2)
- CSV: 15s → 12s ✅
- PDF: 20s → 15s ✅
- Throughput: 20x increase ✅

---

## ⚠️ Rollback (if needed)

```python
# 1. Revert model
modelId="anthropic.claude-3-5-sonnet-20240620-v1:0"

# 2. Restore prompts
copy prompt_original.txt prompt.txt
copy prompt_narrative_original.txt prompt_narrative.txt

# 3. Redeploy
terraform apply
```

---

## 📊 Monitoring

### CloudWatch Logs Query
```
fields @timestamp, complaint_id, timings.total
| filter @message like /timings/
| stats avg(timings.total) as avg_time
```

### Key Metrics
- Lambda Duration: Should drop 60-70%
- Bedrock Calls: Should see Haiku model
- Error Rate: Should stay same or lower
- Cost per Complaint: Should drop 90%

---

## 🎓 Documentation

| Document | Purpose |
|----------|---------|
| `OPTIMIZATION_SUMMARY.md` | Executive overview |
| `IMPLEMENTATION_GUIDE.md` | Step-by-step instructions |
| `LATENCY_OPTIMIZATION_ANALYSIS.md` | Technical deep dive |
| `BEFORE_AFTER_COMPARISON.md` | Visual comparison |
| `OPTIMIZED_lambda_function.py` | Reference implementation |

---

## ✅ Testing Checklist

- [ ] Backup current code
- [ ] Test single narrative
- [ ] Test single PDF
- [ ] Test CSV with 10 complaints
- [ ] Verify all fields extracted
- [ ] Check CloudWatch logs
- [ ] Monitor error rates
- [ ] Validate cost reduction

---

## 💡 Pro Tips

1. **Start Small**: Test with 1 complaint before batches
2. **Monitor Closely**: Watch CloudWatch for first hour
3. **Keep Backups**: Save original files before changes
4. **Test Accuracy**: Compare Haiku vs Sonnet on 100 samples
5. **Gradual Scale**: Start batch_size=5, then increase to 10

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Haiku accuracy low | Revert to Sonnet, use prompt caching |
| Bedrock throttling | Reduce max_workers to 5 |
| DB connection errors | Increase pool max_size |
| Lambda timeout | Check CloudWatch for bottleneck |

---

## 📞 Support

1. Check CloudWatch logs first
2. Review IMPLEMENTATION_GUIDE.md
3. Test with single complaint
4. Keep original files for rollback

---

## 🎯 Success Criteria

✅ Processing time reduced by 50%+
✅ No increase in error rate
✅ All fields extracted correctly
✅ Cost reduced by 80%+
✅ Throughput increased 10x+

---

## 🚦 Status Indicators

### Green (Good to Go)
- Processing time < 20s
- Error rate < 2%
- Extraction accuracy > 90%

### Yellow (Monitor)
- Processing time 20-30s
- Error rate 2-5%
- Extraction accuracy 85-90%

### Red (Rollback)
- Processing time > 30s
- Error rate > 5%
- Extraction accuracy < 85%

---

## 📅 Timeline

| Day | Task | Duration |
|-----|------|----------|
| Day 1 | Phase 1 (Quick Wins) | 1 hour |
| Day 1 | Testing & Validation | 2 hours |
| Day 2-3 | Phase 2 (Optimizations) | 4 hours |
| Day 3 | Load Testing | 2 hours |
| Week 1 | Monitor & Fine-tune | Ongoing |

---

## 💰 Cost Impact

| Item | Before | After | Savings |
|------|--------|-------|---------|
| Per Complaint | $0.058 | $0.006 | 90% |
| 10K/month | $580 | $60 | $520 |
| 100K/month | $5,800 | $600 | $5,200 |

---

## 🎉 Quick Win Summary

**Time Investment:** 1 hour
**Performance Gain:** 50-60% faster
**Cost Savings:** 90% reduction
**Risk Level:** Low
**Rollback Time:** < 1 hour

**Action:** Implement Phase 1 today!
