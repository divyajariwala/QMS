# File Mapping for 3-Step Extraction Process

## Active Files (New Implementation)

### PDF Processing
| Step | Prompt File | Toolspec File | Tool Name |
|------|-------------|---------------|-----------|
| 1 | `prompt_step1.txt` | `toolspec_step1.json` | `extract_case_basic_info` |
| 2 | `prompt_narrative_step2_criticality.txt` | `toolspec_narrative_step2.json` | `extract_criticality` |
| 3 | `prompt_narrative_step3_classification.txt` | `toolspec_narrative_step3.json` | `extract_classification` |

### Narrative Processing
| Step | Prompt File | Toolspec File | Tool Name |
|------|-------------|---------------|-----------|
| 1 | `prompt_narrative_step1.txt` | `toolspec_narrative_step1.json` | `extract_narrative_basic_info` |
| 2 | `prompt_narrative_step2_criticality.txt` | `toolspec_narrative_step2.json` | `extract_criticality` |
| 3 | `prompt_narrative_step3_classification.txt` | `toolspec_narrative_step3.json` | `extract_classification` |

## Deprecated Files (Kept for Reference)
- `prompt.txt` - Original PDF prompt (single-step)
- `prompt_narrative.txt` - Original narrative prompt (single-step)
- `toolspec.json` - Original PDF toolspec
- `toolspec_narrative.json` - Original narrative toolspec

## Original Backup Files
- `prompt_original.txt` - Original PDF prompt backup
- `prompt_narrative_original.txt` - Original narrative prompt backup

## Core Lambda Files
- `lambda_function.py` - Main handler with 3-step chaining logic
- `secrets_util.py` - Database credentials helper
- `requirements.txt` - Python dependencies

## Documentation
- `EXTRACTION_PROCESS_README.md` - Architecture and process overview
- `FILE_MAPPING.md` - This file
