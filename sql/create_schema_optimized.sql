-- MLB QBench PostgreSQL Schema with pgvector support
-- Optimized for text-embedding-3-small (1536 dimensions) with full indexing support
-- Cleaned up version removing unused code and commented sections

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- For text search optimization

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS test_steps CASCADE;
DROP TABLE IF EXISTS test_documents CASCADE;

-- Main test documents table with vector embedding
CREATE TABLE test_documents (
    id SERIAL PRIMARY KEY,
    test_case_id INTEGER UNIQUE NOT NULL,
    uid VARCHAR(255) UNIQUE NOT NULL,
    jira_key VARCHAR(50),
    title TEXT NOT NULL,
    description TEXT,
    summary TEXT,
    
    -- Vector embedding for document-level search (OpenAI text-embedding-3-small)
    embedding vector(1536),
    
    -- Metadata fields
    test_type VARCHAR(50),
    priority VARCHAR(20),
    platforms TEXT[],
    tags TEXT[],
    folder_structure TEXT,
    
    -- TestRail references
    suite_id INTEGER,
    section_id INTEGER,
    project_id INTEGER,
    
    -- Source tracking
    source VARCHAR(255),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional TestRail fields
    is_automated BOOLEAN DEFAULT FALSE,
    refs TEXT,
    custom_fields JSONB
);

-- Test steps table with vector embeddings
CREATE TABLE test_steps (
    id SERIAL PRIMARY KEY,
    test_document_id INTEGER NOT NULL REFERENCES test_documents(id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,
    action TEXT,
    expected TEXT[],
    data TEXT,
    
    -- Vector embedding for step-level search
    embedding vector(1536),
    
    -- Ensure unique steps per test
    UNIQUE(test_document_id, step_index)
);

-- Create indexes for performance

-- B-tree indexes for lookups
CREATE INDEX idx_test_docs_jira_key ON test_documents(jira_key);
CREATE INDEX idx_test_docs_priority ON test_documents(priority);
CREATE INDEX idx_test_docs_test_type ON test_documents(test_type);
CREATE INDEX idx_test_docs_suite_id ON test_documents(suite_id);
CREATE INDEX idx_test_docs_section_id ON test_documents(section_id);
CREATE INDEX idx_test_docs_project_id ON test_documents(project_id);
CREATE INDEX idx_test_docs_test_case_id ON test_documents(test_case_id);

-- GIN indexes for array fields
CREATE INDEX idx_test_docs_tags ON test_documents USING GIN(tags);
CREATE INDEX idx_test_docs_platforms ON test_documents USING GIN(platforms);

-- Text search indexes
CREATE INDEX idx_test_docs_title_trgm ON test_documents USING GIN(title gin_trgm_ops);
CREATE INDEX idx_test_docs_description_trgm ON test_documents USING GIN(description gin_trgm_ops);

-- JSONB index for custom fields
CREATE INDEX idx_test_docs_custom_fields ON test_documents USING GIN(custom_fields);

-- Vector indexes - HNSW for fast approximate nearest neighbor search
CREATE INDEX idx_test_docs_embedding ON test_documents 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_test_steps_embedding ON test_steps 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Helper functions for search operations

-- Function to perform hybrid search combining vector similarity and metadata filters
CREATE OR REPLACE FUNCTION hybrid_search(
    query_embedding vector(1536),
    filter_priority TEXT DEFAULT NULL,
    filter_tags TEXT[] DEFAULT NULL,
    filter_platforms TEXT[] DEFAULT NULL,
    filter_folder TEXT DEFAULT NULL,
    search_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    id INTEGER,
    test_case_id INTEGER,
    uid VARCHAR,
    jira_key VARCHAR,
    title TEXT,
    description TEXT,
    similarity FLOAT,
    priority VARCHAR,
    tags TEXT[],
    folder_structure TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        td.id,
        td.test_case_id,
        td.uid,
        td.jira_key,
        td.title,
        td.description,
        1 - (td.embedding <=> query_embedding) as similarity,
        td.priority,
        td.tags,
        td.folder_structure
    FROM test_documents td
    WHERE 
        (filter_priority IS NULL OR td.priority = filter_priority) AND
        (filter_tags IS NULL OR td.tags && filter_tags) AND
        (filter_platforms IS NULL OR td.platforms && filter_platforms) AND
        (filter_folder IS NULL OR td.folder_structure LIKE filter_folder || '%')
    ORDER BY td.embedding <=> query_embedding
    LIMIT search_limit;
END;
$$ LANGUAGE plpgsql;

-- Function for similarity search on test steps
CREATE OR REPLACE FUNCTION search_steps(
    query_embedding vector(1536),
    search_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    step_id INTEGER,
    test_document_id INTEGER,
    step_index INTEGER,
    action TEXT,
    expected TEXT[],
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ts.id as step_id,
        ts.test_document_id,
        ts.step_index,
        ts.action,
        ts.expected,
        1 - (ts.embedding <=> query_embedding) as similarity
    FROM test_steps ts
    ORDER BY ts.embedding <=> query_embedding
    LIMIT search_limit;
END;
$$ LANGUAGE plpgsql;

-- Function for upserting test documents (idempotent operation)
CREATE OR REPLACE FUNCTION upsert_test_document(
    p_test_case_id INTEGER,
    p_uid VARCHAR,
    p_title TEXT,
    p_embedding vector(1536),
    p_jira_key VARCHAR DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_summary TEXT DEFAULT NULL,
    p_test_type VARCHAR DEFAULT NULL,
    p_priority VARCHAR DEFAULT NULL,
    p_platforms TEXT[] DEFAULT NULL,
    p_tags TEXT[] DEFAULT NULL,
    p_folder_structure TEXT DEFAULT NULL,
    p_suite_id INTEGER DEFAULT NULL,
    p_section_id INTEGER DEFAULT NULL,
    p_project_id INTEGER DEFAULT NULL,
    p_source VARCHAR DEFAULT NULL,
    p_is_automated BOOLEAN DEFAULT FALSE,
    p_refs TEXT DEFAULT NULL,
    p_custom_fields JSONB DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    doc_id INTEGER;
BEGIN
    INSERT INTO test_documents (
        test_case_id, uid, title, embedding, jira_key, description, summary,
        test_type, priority, platforms, tags, folder_structure,
        suite_id, section_id, project_id, source, is_automated, refs, custom_fields
    ) VALUES (
        p_test_case_id, p_uid, p_title, p_embedding, p_jira_key, p_description, p_summary,
        p_test_type, p_priority, p_platforms, p_tags, p_folder_structure,
        p_suite_id, p_section_id, p_project_id, p_source, p_is_automated, p_refs, p_custom_fields
    )
    ON CONFLICT (uid) DO UPDATE SET
        title = EXCLUDED.title,
        embedding = EXCLUDED.embedding,
        jira_key = COALESCE(EXCLUDED.jira_key, test_documents.jira_key),
        description = COALESCE(EXCLUDED.description, test_documents.description),
        summary = COALESCE(EXCLUDED.summary, test_documents.summary),
        test_type = COALESCE(EXCLUDED.test_type, test_documents.test_type),
        priority = COALESCE(EXCLUDED.priority, test_documents.priority),
        platforms = COALESCE(EXCLUDED.platforms, test_documents.platforms),
        tags = COALESCE(EXCLUDED.tags, test_documents.tags),
        folder_structure = COALESCE(EXCLUDED.folder_structure, test_documents.folder_structure),
        is_automated = COALESCE(EXCLUDED.is_automated, test_documents.is_automated),
        refs = COALESCE(EXCLUDED.refs, test_documents.refs),
        custom_fields = COALESCE(EXCLUDED.custom_fields, test_documents.custom_fields),
        updated_at = CURRENT_TIMESTAMP
    RETURNING id INTO doc_id;
    
    RETURN doc_id;
END;
$$ LANGUAGE plpgsql;

-- Create update trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_test_documents_updated_at 
    BEFORE UPDATE ON test_documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();