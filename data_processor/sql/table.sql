CREATE TABLE extensions (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(32) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    desc_summary TEXT,
    description TEXT,
    extension_type SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_extension_type CHECK (extension_type IN (0, 1, 2)),
    CONSTRAINT extension_type_description CHECK (
        CASE
            WHEN extension_type = 0 THEN 'Chrome Extension'
            WHEN extension_type = 1 THEN 'Firefox Add-on'
            WHEN extension_type = 2 THEN 'Safari Extension'
        END IS NOT NULL
    )
);

ALTER TABLE usage_stats
ALTER COLUMN rate DROP NOT NULL,
ALTER COLUMN user_count DROP NOT NULL,
ALTER COLUMN rate_count DROP NOT NULL;

CREATE TABLE usage_stats (
    id SERIAL PRIMARY KEY,
    extension_item_id VARCHAR(32) NOT NULL,
    rate DECIMAL(2,1) CHECK (rate IS NULL OR (rate >= 0 AND rate <= 5)),
    user_count INTEGER,
    rate_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (extension_item_id) REFERENCES extensions(item_id)
);


ALTER TABLE usage_stats
ALTER COLUMN rate DROP NOT NULL,
ALTER COLUMN user_count DROP NOT NULL,
ALTER COLUMN rate_count DROP NOT NULL;
