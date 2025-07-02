from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = "postgresql://text2sql:text2sql@localhost:5432/text2sql_db"
engine = create_engine(DATABASE_URL)

def init_db():
    # Create tables
    with engine.connect() as connection:
        # Create users table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                age INTEGER
            );
        """))
        
        # Create orders table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                product_name VARCHAR(100),
                amount DECIMAL(10,2),
                order_date TIMESTAMP
            );
        """))
        
        # Insert sample data
        connection.execute(text("""
            INSERT INTO users (name, email, age) VALUES
            ('John Doe', 'john@example.com', 30),
            ('Jane Smith', 'jane@example.com', 25),
            ('Bob Johnson', 'bob@example.com', 35)
            ON CONFLICT DO NOTHING;
        """))
        
        connection.execute(text("""
            INSERT INTO orders (user_id, product_name, amount, order_date) VALUES
            (1, 'Laptop', 999.99, '2023-01-15 10:00:00'),
            (1, 'Mouse', 29.99, '2023-01-15 10:00:00'),
            (2, 'Monitor', 299.99, '2023-02-01 14:30:00'),
            (3, 'Keyboard', 79.99, '2023-02-15 09:15:00')
            ON CONFLICT DO NOTHING;
        """))
        
        connection.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized with sample data!") 