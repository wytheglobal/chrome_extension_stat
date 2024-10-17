CREATE TABLE extensions (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(32) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    desc_summary TEXT,
    description TEXT,
    extension_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_counts (
    id SERIAL PRIMARY KEY,
    extension_item_id VARCHAR(32) NOT NULL,
    user_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (extension_item_id) REFERENCES extensions(item_id)
);
