# =============================================
# DATABASE CONNECTION MODULE
# =============================================
import sys
import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import config

# Connection pool for better performance
connection_pool = None

def init_connection_pool():
    """Initialize database connection pool"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # minconn
            10,  # maxconn
            **config.DB_CONFIG
        )
        return True
    except Exception as e:
        print(f"Error creating connection pool: {e}")
        return False

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    if connection_pool is None:
        init_connection_pool()
    
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=False):
    """Context manager for database cursors"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

def execute_query(query, params=None, fetch=True):
    """
    Execute a SQL query
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch: Whether to fetch results
        
    Returns:
        Query results if fetch=True, None otherwise
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return None
    except Exception as e:
        print(f"Query error: {e}")
        raise e

def execute_query_dict(query, params=None):
    """
    Execute query and return results as list of dictionaries
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        List of dictionaries with column names as keys
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            cursor.close()
            return [dict(zip(columns, row)) for row in results]
    except Exception as e:
        print(f"Query error: {e}")
        raise e

def execute_update(query, params=None):
    """
    Execute an INSERT, UPDATE, or DELETE query
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        Number of affected rows
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    except Exception as e:
        print(f"Update error: {e}")
        raise e

def execute_many(query, params_list):
    """
    Execute query with multiple parameter sets
    
    Args:
        query: SQL query string
        params_list: List of parameter tuples
        
    Returns:
        Number of affected rows
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    except Exception as e:
        print(f"Batch insert error: {e}")
        raise e

def test_connection():
    """Test database connection"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"Connected to: {version}")
            return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
