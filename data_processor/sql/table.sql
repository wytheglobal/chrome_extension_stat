CREATE TABLE extension (
    id SERIAL PRIMARY KEY,
    extension_id VARCHAR(32) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    logo TEXT,
    desc_summary TEXT,
    description TEXT,
    category VARCHAR(50),
    version VARCHAR(20),
    version_size VARCHAR(20),
    version_updated_at TIMESTAMP WITH TIME ZONE,
    extension_type SMALLINT NOT NULL DEFAULT 0,
    is_available SMALLINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_item_type CHECK (extension_type IN (0, 1, 2))
);

CREATE TABLE usage_stat (
    id SERIAL PRIMARY KEY,
    extension_id VARCHAR(32) NOT NULL,
    rate DECIMAL(2,1) CHECK (rate IS NULL OR (rate >= 0 AND rate <= 5)),
    user_count INTEGER,
    rate_count INTEGER,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (extension_id) REFERENCES extension(extension_id)
);

CREATE INDEX idx_extension_category ON extension(category);
-- CREATE INDEX idx_extension_version_updated ON extension(version_updated);
CREATE INDEX idx_usage_stat_captured_at ON usage_stat(captured_at);
