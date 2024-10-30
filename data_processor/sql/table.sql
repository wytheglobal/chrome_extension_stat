CREATE TABLE extensions (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(32) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    logo TEXT,
    desc_summary TEXT,
    description TEXT,
    category VARCHAR(50),
    version VARCHAR(20),
    version_size VARCHAR(20),
    version_updated TIMESTAMP WITH TIME ZONE,
    item_type SMALLINT NOT NULL DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_item_type CHECK (item_type IN (0, 1, 2))
);

CREATE TABLE usage_stats (
    id SERIAL PRIMARY KEY,
    extension_item_id VARCHAR(32) NOT NULL,
    rate DECIMAL(2,1) CHECK (rate IS NULL OR (rate >= 0 AND rate <= 5)),
    user_count INTEGER,
    rate_count INTEGER,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (extension_item_id) REFERENCES extensions(item_id)
);

CREATE INDEX idx_extensions_category ON extensions(category);
CREATE INDEX idx_extensions_version_updated ON extensions(version_updated);
CREATE INDEX idx_usage_stats_captured_at ON usage_stats(captured_at);
