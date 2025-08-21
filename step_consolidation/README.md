# Step Field Consolidation Project

## Overview
This project consolidates fragmented step fields from the TestRail database into a single unified field.

## Directory Structure
```
step_consolidation/
├── scripts/       # Python scripts for consolidation
├── data/         # Database files (working copies)
├── logs/         # Process logs and error tracking
├── reports/      # Analysis reports and metrics
└── backup/       # Original database backups
```

## Key Principles
1. **Data Preservation**: Original testrail_data.db is never modified
2. **Accuracy First**: Prioritize correctness over performance
3. **Resumability**: Support checkpoint/resume for interrupted processes
4. **Null Handling**: Leave null for missing steps, include partial data for incomplete

## Database Fields
- `steps`: Summary/abbreviated test steps
- `steps_separated`: JSON array with content/expected pairs
- `steps_combined`: Often contains preconditions (GIVEN statements)
- `consolidated_steps`: NEW - Unified field containing all information

## Process Phases
1. Analysis & Understanding
2. Algorithm Design
3. Implementation
4. Migration & Verification