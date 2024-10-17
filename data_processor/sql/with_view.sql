-- Extensions table
CREATE TABLE extensions (
    extension_id VARCHAR(32) PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    desc_summary TEXT,
    description TEXT,
    extension_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- User counts table
CREATE TABLE user_counts (
    extension_id VARCHAR(32),
    user_count INT UNSIGNED NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (extension_id, timestamp),
    FOREIGN KEY (extension_id) REFERENCES extensions(extension_id)
);

-- Index for faster queries on user_counts
CREATE INDEX idx_user_counts_timestamp ON user_counts(timestamp);

-- View for latest user counts
CREATE VIEW latest_user_counts AS
SELECT uc.extension_id, uc.user_count, uc.timestamp
FROM user_counts uc
INNER JOIN (
    SELECT extension_id, MAX(timestamp) as max_timestamp
    FROM user_counts
    GROUP BY extension_id
) latest ON uc.extension_id = latest.extension_id AND uc.timestamp = latest.max_timestamp;