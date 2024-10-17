import pytest
import json
import os
from psycopg2 import sql, extras
from kafka_consumer import insert_extensions_batch, insert_usage_stats_batch
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED
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
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    yield conn
    conn.close()

@pytest.fixture
def db_cursor(db_connection):
    conn = db_connection
    # Reset the isolation level to READ COMMITTED
    # This ensures that the transaction only sees data committed before the transaction began,
    # preventing dirty reads but allowing non-repeatable reads and phantom reads
    conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
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
    db_cursor.execute("SELECT COUNT(*) FROM extensions")
    prev_count = db_cursor.fetchone()[0]

    insert_extensions_batch(db_cursor, extensions_data)
    need_insert_count = len(extensions_data)
    # db_connection.commit()

    # Verify the data was inserted correctly
    count = db_cursor.execute("SELECT COUNT(*) FROM extensions")
    count = db_cursor.fetchone()[0]
    assert count == prev_count + need_insert_count


    db_cursor.execute("SELECT item_id, name FROM extensions WHERE item_id IN ('bfgdeiadkckfbkeigkoncpdieiiefpig', 'lifbcibllhkdhoafpjfnlhfpfgnpldfl', 'edcbdhndiniiafhoaoljbmhbmchadhmg')")
    results = db_cursor.fetchall()
    assert len(results) == 3
    assert ('bfgdeiadkckfbkeigkoncpdieiiefpig', 'Bitmoji') in results
    assert ('lifbcibllhkdhoafpjfnlhfpfgnpldfl', 'Skype') in results
    assert ('edcbdhndiniiafhoaoljbmhbmchadhmg', 'This item is not available') in results
# def test_insert_usage_stats_batch(db_cursor, db_connection, extensions_data):
    
    db_cursor.execute("SELECT COUNT(*) FROM usage_stats")
    prev_count = db_cursor.fetchone()[0]

    insert_usage_stats_batch(db_cursor, extensions_data)
    # db_connection.commit()

    # Verify the data was inserted correctly
    db_cursor.execute("SELECT COUNT(*) FROM usage_stats")
    count = db_cursor.fetchone()[0]
    assert count == prev_count + need_insert_count

    
    db_cursor.execute("SELECT extension_item_id, rate, user_count FROM usage_stats WHERE extension_item_id IN ('bfgdeiadkckfbkeigkoncpdieiiefpig', 'lifbcibllhkdhoafpjfnlhfpfgnpldfl', 'edcbdhndiniiafhoaoljbmhbmchadhmg')")
    results = db_cursor.fetchall()
    print(results)
    assert ('bfgdeiadkckfbkeigkoncpdieiiefpig', Decimal('3.7'), 4000000) in results
    assert ('lifbcibllhkdhoafpjfnlhfpfgnpldfl', Decimal('3.5'), 3000000) in results
    assert ('edcbdhndiniiafhoaoljbmhbmchadhmg', None, None) in results