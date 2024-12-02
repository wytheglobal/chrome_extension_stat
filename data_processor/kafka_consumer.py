import json
from kafka import KafkaConsumer
import psycopg2
from psycopg2 import sql, extras
from datetime import datetime
import time
from psycopg2.pool import SimpleConnectionPool

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']  # Replace with your Kafka broker(s)
KAFKA_TOPIC = 'browser_extension_raw_data'  # Replace with your topic name
KAFKA_CONSUMER_GROUP = 'extension_processor_v2'

# PostgreSQL configuration
DB_NAME = 'postgres'
DB_USER = 'postgres.eewsowjfvtrukgaglfwu'
DB_PASSWORD = 'AR6sNAW.eX9uBRy'
DB_HOST = 'aws-0-ap-northeast-1.pooler.supabase.com'
DB_PORT = '5432'

# Batch processing configuration
BATCH_SIZE = 50
FLUSH_INTERVAL = 10  # seconds

def create_kafka_consumer():
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=KAFKA_CONSUMER_GROUP,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        max_poll_records=BATCH_SIZE
    )

def create_db_pool(min_conn=1, max_conn=10):
    return SimpleConnectionPool(
        min_conn,
        max_conn,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def insert_extensions_batch(cursor, extensions_data):
    query = sql.SQL("""
        INSERT INTO extension (
            extension_id, url, name, logo, desc_summary, description, 
            category, version, version_size, version_updated_at, 
            extension_type, is_available
        )
        VALUES %s
        ON CONFLICT (extension_id) DO UPDATE
        SET url = EXCLUDED.url,
            name = EXCLUDED.name,
            logo = EXCLUDED.logo,
            desc_summary = EXCLUDED.desc_summary,
            description = EXCLUDED.description,
            category = EXCLUDED.category,
            version = EXCLUDED.version,
            version_size = EXCLUDED.version_size,
            version_updated_at = EXCLUDED.version_updated_at,
            is_available = EXCLUDED.is_available,
            updated_at = CURRENT_TIMESTAMP
    """)
    
    extensions_values = [
        (
            ext['extension_id'],
            ext['url'],
            ext['name'],
            ext.get('logo'),
            ext.get('desc_summary'),
            ext.get('description'),
            ext.get('category'),
            ext.get('version'),
            ext.get('version_size'),
            ext.get('version_updated'),
            0,  # item_type
            2 if ext['name'] == 'This item is not available' else 1, # is_available
        ) for ext in extensions_data
    ]
    extras.execute_values(cursor, query, extensions_values)

def insert_usage_stats_batch(cursor, usage_stats_data):
    query = sql.SQL("""
        INSERT INTO usage_stat (
            extension_id, rate, user_count, rate_count
        )
        VALUES %s
    """)
    
    usage_stats_values = [
        (
            stats['extension_id'],
            stats.get('rate'),
            stats.get('user_count'),
            stats.get('rate_count')
        ) for stats in usage_stats_data if any(stats.get(field) is not None 
            for field in ['rate', 'user_count', 'rate_count'])
    ]
    
    if usage_stats_values:
        extras.execute_values(cursor, query, usage_stats_values)

def process_batch(messages, db_pool):
    extensions_data = []
    usage_stats_data = []

    for message in messages:
        extension_data = message.value
        extensions_data.append(extension_data)
        usage_stats_data.append(extension_data)

    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            insert_extensions_batch(cursor, extensions_data)
            insert_usage_stats_batch(cursor, usage_stats_data)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error processing batch: {e}")
    finally:
        db_pool.putconn(conn)

    print(f"Processed batch of {len(messages)} messages")

def main():
    consumer = create_kafka_consumer()
    db_pool = create_db_pool()

    batch = []
    last_flush_time = time.time()

    print("Starting the consumer...")
    message_count = 0

    try:
        for message in consumer:
            batch.append(message)
            message_count += 1

            if len(batch) >= BATCH_SIZE or (time.time() - last_flush_time) >= FLUSH_INTERVAL:
                print("Processing batch...")
                process_batch(batch, db_pool)
                batch = []
                last_flush_time = time.time()
            
            print(f"Processed {message_count} messages")

    except KeyboardInterrupt:
        print("Stopping the consumer...")
    finally:
        if batch:
            process_batch(batch, db_pool)
        consumer.close()
        db_pool.closeall()

if __name__ == "__main__":
    main()
