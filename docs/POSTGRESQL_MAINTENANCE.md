# PostgreSQL + pgvector Maintenance Guide
## MLB QBench Database Operations and Monitoring

This guide covers ongoing maintenance, monitoring, and operational procedures for the MLB QBench PostgreSQL database with pgvector extension.

---

## 1. DAILY OPERATIONS

### Database Health Checks
```bash
# Check database connection and basic stats
make check-env
curl -s http://localhost:8000/healthz | jq

# Verify pgvector extension is loaded
psql -U postgres -d mlb_qbench -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Check current database size and usage
psql -U postgres -d mlb_qbench -c "
SELECT 
    pg_size_pretty(pg_database_size('mlb_qbench')) as db_size,
    (SELECT count(*) FROM test_documents) as document_count,
    (SELECT count(*) FROM test_steps) as step_count;
"
```

### Performance Monitoring
```sql
-- Monitor vector search performance
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%embedding%';

-- Check connection pool status
SELECT 
    state,
    count(*) as connection_count
FROM pg_stat_activity 
WHERE datname = 'mlb_qbench'
GROUP BY state;

-- Monitor slow queries (if log_min_duration_statement is set)
SELECT 
    mean_exec_time,
    calls,
    query
FROM pg_stat_statements 
WHERE query LIKE '%embedding%'
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

### Index Maintenance
```sql
-- Check index bloat and health
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes 
WHERE tablename IN ('test_documents', 'test_steps')
ORDER BY pg_relation_size(indexrelid) DESC;

-- Rebuild HNSW indexes if necessary (rare, but useful after major data changes)
-- Note: This will temporarily impact search performance
REINDEX INDEX CONCURRENTLY idx_test_documents_embedding;
REINDEX INDEX CONCURRENTLY idx_test_steps_embedding;
```

---

## 2. BACKUP AND RECOVERY

### Automated Daily Backups
```bash
#!/bin/bash
# daily_backup.sh - Add to crontab: 0 2 * * * /path/to/daily_backup.sh

BACKUP_DIR="/backups/mlb_qbench"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mlb_qbench_backup_${DATE}.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform backup with compression
pg_dump -U postgres -h localhost -d mlb_qbench \
    --verbose \
    --format=custom \
    --no-owner \
    --no-privileges \
    --file="$BACKUP_DIR/$BACKUP_FILE"

# Compress the backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "mlb_qbench_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### Vector Data Backup
```bash
# Backup with vector data preservation
pg_dump -U postgres -d mlb_qbench \
    --format=custom \
    --compress=9 \
    --file="mlb_qbench_vectors_$(date +%Y%m%d).backup"

# Restore from backup
pg_restore -U postgres -d mlb_qbench_new \
    --clean \
    --if-exists \
    --verbose \
    mlb_qbench_vectors_20250817.backup
```

### Point-in-Time Recovery Setup
```bash
# Enable WAL archiving in postgresql.conf
archive_mode = on
archive_command = 'cp %p /archives/%f'
wal_level = replica
max_wal_senders = 3
checkpoint_timeout = 5min
```

---

## 3. PERFORMANCE OPTIMIZATION

### Memory Configuration
```ini
# postgresql.conf optimizations for vector workloads
shared_buffers = 2GB                    # 25% of system RAM
effective_cache_size = 6GB              # 75% of system RAM
work_mem = 256MB                        # For sort/hash operations
maintenance_work_mem = 1GB              # For index builds
random_page_cost = 1.1                  # For SSD storage
effective_io_concurrency = 200          # For SSD storage

# Vector-specific settings
max_connections = 100                   # Adjust based on load
shared_preload_libraries = 'pg_stat_statements'
```

### Query Optimization
```sql
-- Analyze tables for optimal query planning
ANALYZE test_documents;
ANALYZE test_steps;

-- Update table statistics
UPDATE pg_statistic SET starelid = 'test_documents'::regclass WHERE starelid = 'test_documents'::regclass;

-- Monitor query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM test_documents 
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector 
LIMIT 10;
```

### Index Tuning
```sql
-- HNSW index parameters for different use cases
-- For accuracy-focused workloads:
CREATE INDEX idx_embedding_high_accuracy ON test_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 32, ef_construction = 128);

-- For speed-focused workloads:
CREATE INDEX idx_embedding_fast ON test_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- For memory-constrained environments:
CREATE INDEX idx_embedding_compact ON test_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);
```

---

## 4. MONITORING AND ALERTING

### Key Metrics to Monitor
```bash
# Database size growth
psql -U postgres -d mlb_qbench -c "
SELECT pg_size_pretty(pg_database_size('mlb_qbench')) as current_size;
"

# Connection pool utilization
psql -U postgres -d mlb_qbench -c "
SELECT 
    count(*) as active_connections,
    max_conn,
    (count(*)::float / max_conn * 100)::int as utilization_percent
FROM pg_stat_activity, 
     (SELECT setting::int as max_conn FROM pg_settings WHERE name = 'max_connections') s
WHERE state = 'active';
"

# Vector search performance
curl -s http://localhost:8000/metrics | jq '.database'
```

### Automated Monitoring Script
```bash
#!/bin/bash
# monitor_qbench.sh - Run every 5 minutes via cron

# Set thresholds
MAX_CONNECTIONS=80
MAX_DB_SIZE_GB=50
MIN_SEARCH_PERFORMANCE_MS=1000

# Check database size
DB_SIZE_MB=$(psql -U postgres -d mlb_qbench -t -c "SELECT pg_database_size('mlb_qbench')/1024/1024;")
if (( ${DB_SIZE_MB%.*} > $((MAX_DB_SIZE_GB * 1024)) )); then
    echo "ALERT: Database size exceeds ${MAX_DB_SIZE_GB}GB: ${DB_SIZE_MB}MB"
fi

# Check connection count
ACTIVE_CONNS=$(psql -U postgres -d mlb_qbench -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
if (( ACTIVE_CONNS > MAX_CONNECTIONS )); then
    echo "ALERT: High connection count: $ACTIVE_CONNS"
fi

# Check API health
RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:8000/healthz)
if (( ${RESPONSE_TIME%.*} > 5 )); then
    echo "ALERT: Slow API response time: ${RESPONSE_TIME}s"
fi
```

---

## 5. TROUBLESHOOTING

### Common Issues and Solutions

#### Slow Vector Searches
```sql
-- Check if indexes are being used
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM test_documents 
ORDER BY embedding <=> $1::vector 
LIMIT 10;

-- If index not used, check statistics
SELECT 
    schemaname, tablename, attname, 
    n_distinct, correlation
FROM pg_stats 
WHERE tablename = 'test_documents' AND attname = 'embedding';

-- Force index usage if needed
SET enable_seqscan = false;
```

#### Connection Pool Exhaustion
```bash
# Check for hanging connections
psql -U postgres -d mlb_qbench -c "
SELECT 
    pid, 
    state, 
    query_start, 
    state_change, 
    query
FROM pg_stat_activity 
WHERE state != 'idle' 
ORDER BY query_start;
"

# Kill hanging connections if necessary
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND state_change < now() - interval '1 hour';"
```

#### High Memory Usage
```sql
-- Check work_mem usage
SELECT 
    pid, 
    query,
    state,
    backend_type
FROM pg_stat_activity 
WHERE backend_type = 'client backend' 
ORDER BY query_start;

-- Check for memory-intensive operations
SELECT 
    query,
    mean_exec_time,
    calls,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC;
```

#### Vector Index Corruption
```sql
-- Check index integrity
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%embedding%';

-- Rebuild corrupted indexes
DROP INDEX IF EXISTS idx_test_documents_embedding;
CREATE INDEX CONCURRENTLY idx_test_documents_embedding 
ON test_documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

## 6. CAPACITY PLANNING

### Scaling Considerations
```sql
-- Current storage usage breakdown
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Growth Projections
- **Current**: ~104k test documents
- **Vector storage**: ~1.5GB per 100k documents (1536-dim embeddings)
- **Index overhead**: ~2x vector data size for HNSW indexes
- **Recommended**: Plan for 500k documents = ~7.5GB vector data + 15GB indexes

### Hardware Recommendations
```bash
# For 500k documents:
RAM: 16GB minimum (32GB recommended)
Storage: 50GB SSD minimum (100GB recommended)
CPU: 4 cores minimum (8 cores recommended)
Network: 1Gbps for distributed deployments
```

---

## 7. MAINTENANCE SCRIPTS

### Weekly Maintenance
```bash
#!/bin/bash
# weekly_maintenance.sh

echo "Starting weekly PostgreSQL maintenance..."

# Analyze all tables for optimal query planning
psql -U postgres -d mlb_qbench -c "ANALYZE;"

# Update table statistics
psql -U postgres -d mlb_qbench -c "
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY schemaname, tablename, attname;
"

# Check for unused indexes
psql -U postgres -d mlb_qbench -c "
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    idx_scan as scans
FROM pg_stat_user_indexes 
WHERE idx_scan < 100
ORDER BY idx_scan;
"

echo "Weekly maintenance completed."
```

### Monthly Deep Maintenance
```bash
#!/bin/bash
# monthly_maintenance.sh

echo "Starting monthly deep maintenance..."

# Vacuum analyze (reclaim space and update statistics)
psql -U postgres -d mlb_qbench -c "VACUUM ANALYZE;"

# Check for bloated tables
psql -U postgres -d mlb_qbench -c "
SELECT 
    schemaname, 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_tup_ins + n_tup_upd + n_tup_del as total_operations
FROM pg_stat_user_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Performance report
python scripts/generate_performance_report.py

echo "Monthly maintenance completed."
```

---

## 8. DISASTER RECOVERY

### Recovery Procedures
```bash
# 1. Assess damage
psql -U postgres -l  # List databases
psql -U postgres -d mlb_qbench -c "\dt"  # List tables

# 2. Restore from latest backup
pg_restore -U postgres -d mlb_qbench_recovery \
    --clean --if-exists --verbose \
    /backups/mlb_qbench/latest_backup.sql.gz

# 3. Verify data integrity
psql -U postgres -d mlb_qbench_recovery -c "
SELECT 
    (SELECT count(*) FROM test_documents) as doc_count,
    (SELECT count(*) FROM test_steps) as step_count,
    (SELECT count(*) FROM test_documents WHERE embedding IS NULL) as missing_embeddings;
"

# 4. Switch application to recovery database
# Update DATABASE_URL in .env file
```

### Emergency Contacts and Procedures
- **Database corruption**: Follow backup restoration procedure above
- **Performance degradation**: Check monitoring scripts in section 4
- **Connection issues**: Restart PostgreSQL service: `sudo systemctl restart postgresql`
- **Disk space issues**: Run vacuum and check backup cleanup scripts

---

## 9. USEFUL COMMANDS REFERENCE

### Development Commands
```bash
# Clear all data (keeps schema)
make db-clear

# Reset database completely  
make postgres-clean

# Test migration with sample data
make migrate-test

# Run full optimized migration
make migrate-optimized

# Check environment configuration
make check-env
```

### PostgreSQL Management
```bash
# Connect to database
psql -U postgres -d mlb_qbench

# Show database sizes
psql -U postgres -c "\l+"

# Show table sizes
psql -U postgres -d mlb_qbench -c "\dt+"

# Show index information
psql -U postgres -d mlb_qbench -c "\di+"

# Monitor active queries
psql -U postgres -d mlb_qbench -c "SELECT pid, query_start, state, query FROM pg_stat_activity WHERE state != 'idle';"
```

### Vector Operations
```sql
-- Test vector similarity
SELECT embedding <=> '[0.1, 0.2, ...]'::vector as distance
FROM test_documents 
LIMIT 5;

-- Check vector dimensions
SELECT vector_dims(embedding) FROM test_documents LIMIT 1;

-- Find null embeddings
SELECT count(*) FROM test_documents WHERE embedding IS NULL;
```

This maintenance guide provides comprehensive operational procedures for keeping the MLB QBench PostgreSQL database healthy and performant.