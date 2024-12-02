import pytest
import json
import os
from psycopg2 import sql, extras
from kafka_consumer import insert_extensions_batch, insert_usage_stats_batch
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_READ_UNCOMMITTED
import psycopg2
from decimal import Decimal


# Load environment variables
load_dotenv()

# Load mock data from JSON file
current_dir = os.path.dirname(os.path.abspath(__file__))
mock_data_path = os.path.join(current_dir, 'mock_data.json')
with open(mock_data_path, 'r') as f:
    mock_data = json.load(f)

@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    # This sets the isolation level to AUTOCOMMIT
    # In AUTOCOMMIT mode, each SQL statement is treated as a separate transaction
    # that is automatically committed after it is executed
    # conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    yield conn
    conn.close()

@pytest.fixture
def db_cursor(db_connection):
    conn = db_connection
    # Reset the isolation level to READ COMMITTED
    # This ensures that the transaction only sees data committed before the transaction began,
    # preventing dirty reads but allowing non-repeatable reads and phantom reads
    conn.set_isolation_level(ISOLATION_LEVEL_READ_UNCOMMITTED)
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN")
        yield cursor
    finally:
        cursor.execute("ROLLBACK")
        cursor.close()

@pytest.fixture
def extensions_data():
    return mock_data

def test_insert_extensions_batch(db_cursor, db_connection, extensions_data):
    db_cursor.execute("SELECT COUNT(*) FROM extension")
    prev_count = db_cursor.fetchone()[0]

    insert_extensions_batch(db_cursor, extensions_data)
    need_insert_count = len(extensions_data)
    # db_connection.commit()

    # Verify the data was inserted correctly
    count = db_cursor.execute("SELECT COUNT(*) FROM extension")
    count = db_cursor.fetchone()[0]
    assert count == prev_count + need_insert_count

    # Verify all records were inserted correctly by checking each item in mock data
    for item in extensions_data:
        db_cursor.execute("""
            SELECT extension_id, url, logo, name, desc_summary, description, 
                   category, version, version_size, version_updated_at, is_available
            FROM extension
            WHERE extension_id = %s
        """, (item['extension_id'],))
        result = db_cursor.fetchone()
        
        assert result is not None
        assert result[0] == item['extension_id']  # extension_id
        assert result[1] == item['url']  # url
        assert result[2] == item.get('logo')  # logo may be null
        assert result[3] == item['name']  # name
        assert result[4] == item.get('desc_summary')  # desc_summary may be null
        assert result[5] == item.get('description')  # description may be null
        assert result[6] == item.get('category')  # category may be null
        assert result[7] == item.get('version')  # version may be null
        assert result[8] == item.get('version_size')  # version_size may be null
        # version_updated requires timestamp comparison which we'll skip for now
        assert result[10] == 2 if item['name'] is 'This item is not available' else 1  # is_available may be null




    # db_cursor.execute("SELECT extension_id, name FROM extensions WHERE extension_id IN ('bfgdeiadkckfbkeigkoncpdieiiefpig', 'lifbcibllhkdhoafpjfnlhfpfgnpldfl', 'edcbdhndiniiafhoaoljbmhbmchadhmg')")
    # results = db_cursor.fetchall()
    # assert len(results) == 3
    # assert ('bfgdeiadkckfbkeigkoncpdieiiefpig', 'Bitmoji') in results
    # assert ('lifbcibllhkdhoafpjfnlhfpfgnpldfl', 'Skype') in results
    # assert ('edcbdhndiniiafhoaoljbmhbmchadhmg', 'This item is not available') in results
# def test_insert_usage_stats_batch(db_cursor, db_connection, extensions_data):
    
    db_cursor.execute("SELECT COUNT(*) FROM usage_stat")
    prev_count = db_cursor.fetchone()[0]

    insert_usage_stats_batch(db_cursor, extensions_data)
    # db_connection.commit()

    # Verify the data was inserted correctly
    db_cursor.execute("SELECT COUNT(*) FROM usage_stat")
    count = db_cursor.fetchone()[0]
    print("================ count", count)
    # has one item is not available, so - 1
    assert count == prev_count + (need_insert_count - 1)

    for item in extensions_data:
        # Skip checking usage stats for unavailable items
        if item['name'] != 'This item is not available':
            db_cursor.execute("""
                SELECT extension_id, rate, user_count, rate_count
                FROM usage_stat
                WHERE extension_id = %s
                ORDER BY captured_at DESC
                LIMIT 1
            """, (item['extension_id'],))
            rows = db_cursor.fetchall()
            print("================")
            print(rows)
            result = rows[0]
            assert result is not None
            assert result[0] == item['extension_id']  # extension_id
            assert float(result[1]) == item.get('rate') if item.get('rate') else result[1] is None  # rate may be null
            assert result[2] == item.get('user_count')  # user_count may be null
            assert result[3] == item.get('rate_count')  # rate_count may be null

    # test multiple insert
    insert_usage_stats_batch(db_cursor, extensions_data)
    for item in extensions_data:
        if item['name'] != 'This item is not available':
            db_cursor.execute("""
                SELECT extension_id, rate, user_count, rate_count
                FROM usage_stat
                WHERE extension_id = %s
                ORDER BY captured_at DESC
                LIMIT 1
            """, (item['extension_id'],))
            rows = db_cursor.fetchall()
            print("================", item['extension_id'])
            print(rows)
            result = rows[0]
            assert result is not None
            assert result[0] == item['extension_id']  # extension_id
            assert float(result[1]) == item.get('rate') if item.get('rate') else result[1] is None  # rate may be null
            assert result[2] == item.get('user_count')  # user_count may be null
            assert result[3] == item.get('rate_count')  # rate_count may be null