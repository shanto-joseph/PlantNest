#!/usr/bin/env python3
"""
Database Creation Script for Plant & Gardening Store
This script creates the MySQL database with proper character set and collation.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database_name': os.getenv('DB_NAME', 'plant_gardening_store'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    return config

def create_database(config):
    """Create the MySQL database with specified character set and collation"""
    connection = None
    
    try:
        # Connect to MySQL server (without specifying database)
        print(f"Connecting to MySQL server at {config['host']}:{config['port']}...")
        connection = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if database already exists
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            if config['database_name'] in databases:
                print(f"Database '{config['database_name']}' already exists.")
                
                # Ask user if they want to recreate it
                response = input("Do you want to drop and recreate it? (y/N): ").lower().strip()
                if response in ['y', 'yes']:
                    print(f"Dropping existing database '{config['database_name']}'...")
                    cursor.execute(f"DROP DATABASE `{config['database_name']}`")
                    print("Database dropped successfully.")
                else:
                    print("Database creation cancelled.")
                    return True
            
            # Create the database with specified character set and collation
            create_db_query = f"""
            CREATE DATABASE `{config['database_name']}` 
            CHARACTER SET {config['charset']} 
            COLLATE {config['collation']}
            """
            
            print(f"Creating database '{config['database_name']}'...")
            print(f"Character Set: {config['charset']}")
            print(f"Collation: {config['collation']}")
            
            cursor.execute(create_db_query)
            print(f"Database '{config['database_name']}' created successfully!")
            
            # Verify database creation
            cursor.execute(f"SHOW CREATE DATABASE `{config['database_name']}`")
            result = cursor.fetchone()
            print(f"Database info: {result[1]}")
            
            # Grant privileges to the user (if not root)
            if config['user'] != 'root':
                grant_query = f"""
                GRANT ALL PRIVILEGES ON `{config['database_name']}`.* 
                TO '{config['user']}'@'%'
                """
                cursor.execute(grant_query)
                cursor.execute("FLUSH PRIVILEGES")
                print(f"Granted all privileges to user '{config['user']}'")
            
            cursor.close()
            return True
            
    except Error as e:
        print(f"Error: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

def test_connection(config):
    """Test connection to the newly created database"""
    try:
        print(f"\nTesting connection to database '{config['database_name']}'...")
        connection = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database_name']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"Successfully connected to database: {current_db}")
            
            # Check character set and collation
            cursor.execute("""
                SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME 
                FROM information_schema.SCHEMATA 
                WHERE SCHEMA_NAME = %s
            """, (config['database_name'],))
            
            charset_info = cursor.fetchone()
            if charset_info:
                print(f"Database character set: {charset_info[0]}")
                print(f"Database collation: {charset_info[1]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"Connection test failed: {e}")
        return False

def main():
    """Main function to create database"""
    print("=" * 60)
    print("Plant & Gardening Store - Database Creation Script")
    print("=" * 60)
    
    # Load configuration
    config = load_environment()
    
    print(f"Configuration:")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  User: {config['user']}")
    print(f"  Database: {config['database_name']}")
    print(f"  Character Set: {config['charset']}")
    print(f"  Collation: {config['collation']}")
    print("-" * 60)
    
    # Check if required environment variables are set
    if not config['user']:
        print("Error: DB_USER environment variable is not set!")
        sys.exit(1)
    
    # Create database
    if create_database(config):
        print("\n✅ Database creation completed successfully!")
        
        # Test connection
        if test_connection(config):
            print("\n✅ Database connection test passed!")
            print("\nNext steps:")
            print("1. Run: python manage.py makemigrations")
            print("2. Run: python manage.py migrate")
            print("3. Run: python manage.py createsuperuser")
            print("4. Run: python manage.py runserver")
        else:
            print("\n❌ Database connection test failed!")
            print("Please check your database configuration.")
    else:
        print("\n❌ Database creation failed!")
        print("Please check your MySQL server and credentials.")
        sys.exit(1)

if __name__ == "__main__":
    main()