import json
from kafka import KafkaConsumer
import psycopg2
from psycopg2 import sql, extras
from datetime import datetime
import time
from psycopg2.pool import SimpleConnectionPool

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']  # Replace with your Kafka broker(s)
KAFKA_TOPIC = 'browser_extension_detail'  # Replace with your topic name

# PostgreSQL configuration
DB_NAME = 'postgres'
DB_USER = 'postgres.eewsowjfvtrukgaglfwu'
DB_PASSWORD = 'AR6sNAW.eX9uBRy'
DB_HOST = 'aws-0-ap-northeast-1.pooler.supabase.com'
DB_PORT = '5432'

# Batch processing configuration
BATCH_SIZE = 10
FLUSH_INTERVAL = 10  # seconds

def create_kafka_consumer():
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='extension_processor',
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
        INSERT INTO extensions (item_id, url, name, desc_summary, description, extension_type)
        VALUES %s
        ON CONFLICT (item_id) DO UPDATE
        SET url = EXCLUDED.url,
            name = EXCLUDED.name,
            desc_summary = EXCLUDED.desc_summary,
            description = EXCLUDED.description,
            extension_type = EXCLUDED.extension_type,
            updated_at = CURRENT_TIMESTAMP
    """)
    extensions_values = [
        (
            ext['extension_id'],
            ext['url'],
            ext['name'],
            ext.get('desc_summary'),
            ext.get('description'),
            'chrome',
        ) for ext in extensions_data
    ]
    extras.execute_values(cursor, query, extensions_values)

def insert_user_counts_batch(cursor, user_counts_data):
    query = sql.SQL("""
        INSERT INTO user_counts (extension_item_id, user_count)
        VALUES %s
    """)
    user_counts_values = [
        (item_id, user_count) for item_id, user_count in user_counts_data
    ]
    extras.execute_values(cursor, query, user_counts_values)

def process_batch(messages, db_pool):
    extensions_data = []
    user_counts_data = []

    for message in messages:
        extension_data = message.value
        extensions_data.append(extension_data)
        user_counts_data.append((extension_data['extension_id'], extension_data['user_count']))

    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            insert_extensions_batch(cursor, extensions_data)
            insert_user_counts_batch(cursor, user_counts_data)
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