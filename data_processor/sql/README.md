

For handling multiple thumbnails, it's better to create a separate table. Here's why:
1. One extension can have multiple thumbnails (one-to-many relationship)
2. Better data normalization
3. Easier to manage and query thumbnail data
4. More flexible for future changes

Here's the modified schema:

```sql:data_processor/sql/table.sql
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

CREATE TABLE extension_thumbnails (
    id SERIAL PRIMARY KEY,
    extension_item_id VARCHAR(32) NOT NULL,
    url TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,  -- To maintain thumbnail order
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (extension_item_id) REFERENCES extensions(item_id)
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

-- Existing indexes
CREATE INDEX idx_extensions_category ON extensions(category);
CREATE INDEX idx_extensions_version_updated ON extensions(version_updated);
CREATE INDEX idx_usage_stats_captured_at ON usage_stats(captured_at);

-- New index for thumbnails
CREATE INDEX idx_extension_thumbnails_item_id ON extension_thumbnails(extension_item_id);
```

Alternative approaches (not recommended):
1. Using an array column in extensions table:
```sql
thumbnails TEXT[]  -- PostgreSQL array type
```
2. Using JSON/JSONB column:
```sql
thumbnails JSONB
```

The separate table approach is better because:
1. Better data integrity with foreign key constraints
2. Easier to query and manage individual thumbnails
3. Can add additional thumbnail metadata later
4. Better performance for large datasets
5. Maintains proper database normalization

Example usage:
```sql
-- Insert thumbnails
INSERT INTO extension_thumbnails (extension_item_id, url, display_order) VALUES
('kdkohcmkkplmkknlelglhfhjkegkiljd', 'https://example.com/thumb1.jpg', 0),
('kdkohcmkkplmkknlelglhfhjkegkiljd', 'https://example.com/thumb2.jpg', 1);

-- Query extension with thumbnails
SELECT e.*, array_agg(t.url ORDER BY t.display_order) as thumbnails
FROM extensions e
LEFT JOIN extension_thumbnails t ON e.item_id = t.extension_item_id
GROUP BY e.id;
```