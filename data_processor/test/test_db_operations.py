import pytest
import psycopg2
from datetime import datetime, timezone
import os
from dotenv import dotenv_values
import json
from kafka_consumer import insert_extensions_batch, insert_usage_stats_batch


# Load environment variables
config = dotenv_values('.env.test')

# Database connection configuration
DB_CONFIG = {
    'dbname': config['DB_NAME'],
    'user': config['DB_USER'],
    'password': config['DB_PASSWORD'],
    'host': config['DB_HOST'],
    'port': config['DB_PORT']
}

@pytest.fixture(scope='session')
def db_schema():
    # Read SQL schema file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_dir, '../sql/table.sql')
    with open(schema_path, 'r') as f:
        return f.read()

@pytest.fixture(scope='function')
def db_connection():
    # Create a test database connection
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    yield conn
    conn.close()

@pytest.fixture(scope='function')
def setup_test_db(db_connection, db_schema):
    cursor = db_connection.cursor()
    
    # Drop existing tables if they exist
    cursor.execute("""
        DROP TABLE IF EXISTS usage_stat;
        DROP TABLE IF EXISTS extension;
    """)
    
    # Create tables using schema
    cursor.execute(db_schema)
    
    yield cursor
    
    # Cleanup after tests
    # cursor.execute("""
    #     DROP TABLE IF EXISTS usage_stat;
    #     DROP TABLE IF EXISTS extension;
    # """)
    cursor.close()

@pytest.fixture
def extensions_data():
    # Load mock data from JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mock_data_path = os.path.join(current_dir, 'mock_data.json')
    with open(mock_data_path, 'r') as f:
        mock_data = json.load(f)
    return mock_data


def test_insert_extension(setup_test_db, extensions_data):
    cursor = setup_test_db

    insert_extensions_batch(cursor, extensions_data)
    insert_usage_stats_batch(cursor, extensions_data)


    # update usage stats
    extensions_data[0]['rate'] = 4.2
    extensions_data[0]['user_count'] = 314159

    insert_extensions_batch(cursor, extensions_data)
    insert_usage_stats_batch(cursor, extensions_data)
    
# def test_insert_usage_stat(setup_test_db):
#     cursor = setup_test_db
    
#     # First insert extension
#     cursor.execute("""
#         INSERT INTO extension (extension_id, url, name, extension_type)
#         VALUES ('test-ext-002', 'https://test.com', 'Test Extension', 0)
#     """)
    
#     # Insert usage stat
#     usage_data = {
#         'extension_id': 'test-ext-002',
#         'rate': 4.5,
#         'user_count': 1000,
#         'rate_count': 100
#     }
    
#     cursor.execute("""
#         INSERT INTO usage_stat (extension_id, rate, user_count, rate_count)
#         VALUES (%(extension_id)s, %(rate)s, %(user_count)s, %(rate_count)s)
#         RETURNING id
#     """, usage_data)
    
#     inserted_id = cursor.fetchone()[0]
    
#     # Verify
#     cursor.execute("SELECT extension_id, rate FROM usage_stat WHERE id = %s", (inserted_id,))
#     result = cursor.fetchone()
    
#     assert result[0] == usage_data['extension_id']
#     assert float(result[1]) == usage_data['rate']

# def test_update_extension(setup_test_db):
#     cursor = setup_test_db
    
#     # Insert test data
#     cursor.execute("""
#         INSERT INTO extension (extension_id, url, name, extension_type)
#         VALUES ('test-ext-003', 'https://test.com', 'Old Name', 0)
#     """)
    
#     # Update
#     cursor.execute("""
#         UPDATE extension 
#         SET name = 'New Name'
#         WHERE extension_id = 'test-ext-003'
#         RETURNING name
#     """)
    
#     updated_name = cursor.fetchone()[0]
#     assert updated_name == 'New Name'

# def test_delete_extension(setup_test_db):
#     cursor = setup_test_db
    
#     # Insert test data
#     cursor.execute("""
#         INSERT INTO extension (extension_id, url, name, extension_type)
#         VALUES ('test-ext-004', 'https://test.com', 'To Delete', 0)
#     """)
    
#     # Delete
#     cursor.execute("""
#         DELETE FROM extension 
#         WHERE extension_id = 'test-ext-004'
#         RETURNING extension_id
#     """)
    
#     deleted_id = cursor.fetchone()[0]
#     assert deleted_id == 'test-ext-004'
    
#     # Verify deletion
#     cursor.execute("SELECT COUNT(*) FROM extension WHERE extension_id = 'test-ext-004'")
#     count = cursor.fetchone()[0]
#     assert count == 0

# def test_constraint_extension_type(setup_test_db):
#     cursor = setup_test_db
    
#     # Test invalid extension_type
#     with pytest.raises(psycopg2.errors.CheckViolation):
#         cursor.execute("""
#             INSERT INTO extension (extension_id, url, name, extension_type)
#             VALUES ('test-ext-005', 'https://test.com', 'Test', 3)
#         """)

# def test_constraint_usage_stat_rate(setup_test_db):
#     cursor = setup_test_db
    
#     # Insert valid extension first
#     cursor.execute("""
#         INSERT INTO extension (extension_id, url, name, extension_type)
#         VALUES ('test-ext-006', 'https://test.com', 'Test Extension', 0)
#     """)
    
#     # Test invalid rate
#     with pytest.raises(psycopg2.errors.CheckViolation):
#         cursor.execute("""
#             INSERT INTO usage_stat (extension_id, rate)
#             VALUES ('test-ext-006', 5.5)
#         """)