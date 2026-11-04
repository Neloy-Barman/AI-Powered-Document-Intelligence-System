CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'uploaded',
    storage_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE image_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    file_type VARCHAR(20) NOT NULL,
    text_content TEXT,
    qdrant_point_id VARCHAR(100),
    bm25_entry_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE tabular_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    file_type VARCHAR(20) NOT NULL,
    sheet_name VARCHAR(255),
    row_count INT NOT NULL,
    column_count INT NOT NULL,
    columns JSONB,
    chunk_index INT NOT NULL,
    chunk_count INT NOT NULL,
    chunk_range JSONB NOT NULL,
    text_content TEXT NOT NULL,
    qdrant_point_id VARCHAR(100),
    bm25_entry_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_file_type ON documents(file_type);
CREATE INDEX idx_image_documents_document_id ON image_documents(document_id);
CREATE INDEX idx_tabular_documents_document_id ON tabular_documents(document_id);
