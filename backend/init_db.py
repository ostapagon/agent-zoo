from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = "postgresql://text2sql:text2sql@localhost:5432/text2sql_db"
engine = create_engine(DATABASE_URL)

def init_db():
    # Create tables
    with engine.connect() as connection:
        # Create categories table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                parent_id INTEGER REFERENCES categories(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create suppliers table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                contact_person VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(20),
                address TEXT,
                country VARCHAR(50),
                rating DECIMAL(3,2) DEFAULT 0.0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create customers table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                address TEXT,
                city VARCHAR(50),
                state VARCHAR(50),
                country VARCHAR(50),
                postal_code VARCHAR(20),
                date_of_birth DATE,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                total_orders INTEGER DEFAULT 0,
                total_spent DECIMAL(12,2) DEFAULT 0.0
            );
        """))
        
        # Create products table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                sku VARCHAR(50) UNIQUE,
                category_id INTEGER REFERENCES categories(id),
                supplier_id INTEGER REFERENCES suppliers(id),
                price DECIMAL(10,2) NOT NULL,
                cost_price DECIMAL(10,2),
                weight_kg DECIMAL(8,3),
                dimensions_cm VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create inventory table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id),
                warehouse_location VARCHAR(100),
                quantity_in_stock INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 10,
                max_stock_level INTEGER DEFAULT 1000,
                last_restocked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create orders table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(id),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pending',
                total_amount DECIMAL(12,2) DEFAULT 0.0,
                shipping_address TEXT,
                billing_address TEXT,
                payment_method VARCHAR(50),
                payment_status VARCHAR(20) DEFAULT 'pending',
                shipping_cost DECIMAL(8,2) DEFAULT 0.0,
                tax_amount DECIMAL(8,2) DEFAULT 0.0,
                discount_amount DECIMAL(8,2) DEFAULT 0.0,
                notes TEXT
            );
        """))
        
        # Create order_items table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id),
                product_id INTEGER REFERENCES products(id),
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                discount_percentage DECIMAL(5,2) DEFAULT 0.0
            );
        """))
        
        # Create product_reviews table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS product_reviews (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id),
                customer_id INTEGER REFERENCES customers(id),
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                review_text TEXT,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_verified_purchase BOOLEAN DEFAULT FALSE
            );
        """))
        
        # Create shipping_methods table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS shipping_methods (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                base_cost DECIMAL(8,2) NOT NULL,
                delivery_time_days INTEGER,
                is_active BOOLEAN DEFAULT TRUE
            );
        """))
        
        # Insert sample data
        insert_sample_data(connection)
        
        connection.commit()

def insert_sample_data(connection):
    # Insert categories
    categories_data = [
        ('Electronics', 'Electronic devices and accessories', None),
        ('Computers', 'Desktop and laptop computers', 1),
        ('Mobile Devices', 'Smartphones and tablets', 1),
        ('Accessories', 'Computer and mobile accessories', 1),
        ('Clothing', 'Apparel and fashion items', None),
        ('Men\'s Clothing', 'Clothing for men', 5),
        ('Women\'s Clothing', 'Clothing for women', 5),
        ('Home & Garden', 'Home improvement and garden items', None),
        ('Furniture', 'Home and office furniture', 8),
        ('Books', 'Books and publications', None),
        ('Fiction', 'Fiction books', 10),
        ('Non-Fiction', 'Non-fiction books', 10)
    ]
    
    for name, description, parent_id in categories_data:
        connection.execute(text("""
            INSERT INTO categories (name, description, parent_id) 
            VALUES (:name, :description, :parent_id)
            ON CONFLICT DO NOTHING
        """), {"name": name, "description": description, "parent_id": parent_id})
    
    # Insert suppliers
    suppliers_data = [
        ('TechCorp Industries', 'John Smith', 'john@techcorp.com', '+1-555-0101', '123 Tech Street, Silicon Valley, CA', 'USA', 4.5),
        ('Global Electronics Ltd', 'Maria Garcia', 'maria@globalelec.com', '+1-555-0102', '456 Electronics Ave, Austin, TX', 'USA', 4.2),
        ('Fashion Forward Inc', 'Sarah Johnson', 'sarah@fashionforward.com', '+1-555-0103', '789 Fashion Blvd, New York, NY', 'USA', 4.0),
        ('Home Essentials Co', 'Mike Wilson', 'mike@homeessentials.com', '+1-555-0104', '321 Home Street, Chicago, IL', 'USA', 4.3),
        ('BookWorld Publishers', 'Lisa Chen', 'lisa@bookworld.com', '+1-555-0105', '654 Book Lane, Seattle, WA', 'USA', 4.7)
    ]
    
    for name, contact, email, phone, address, country, rating in suppliers_data:
        connection.execute(text("""
            INSERT INTO suppliers (name, contact_person, email, phone, address, country, rating)
            VALUES (:name, :contact, :email, :phone, :address, :country, :rating)
            ON CONFLICT DO NOTHING
        """), {"name": name, "contact": contact, "email": email, "phone": phone, "address": address, "country": country, "rating": rating})
    
    # Insert customers
    customers_data = [
        ('Alice', 'Johnson', 'alice.johnson@email.com', '+1-555-0201', '123 Main St, Boston, MA', 'Boston', 'MA', 'USA', '02101', '1990-05-15'),
        ('Bob', 'Williams', 'bob.williams@email.com', '+1-555-0202', '456 Oak Ave, San Francisco, CA', 'San Francisco', 'CA', 'USA', '94102', '1985-08-22'),
        ('Carol', 'Davis', 'carol.davis@email.com', '+1-555-0203', '789 Pine Rd, Miami, FL', 'Miami', 'FL', 'USA', '33101', '1992-03-10'),
        ('David', 'Miller', 'david.miller@email.com', '+1-555-0204', '321 Elm St, Seattle, WA', 'Seattle', 'WA', 'USA', '98101', '1988-11-30'),
        ('Eva', 'Garcia', 'eva.garcia@email.com', '+1-555-0205', '654 Maple Dr, Denver, CO', 'Denver', 'CO', 'USA', '80201', '1995-07-18'),
        ('Frank', 'Brown', 'frank.brown@email.com', '+1-555-0206', '987 Cedar Ln, Portland, OR', 'Portland', 'OR', 'USA', '97201', '1983-12-05'),
        ('Grace', 'Taylor', 'grace.taylor@email.com', '+1-555-0207', '147 Birch Way, Austin, TX', 'Austin', 'TX', 'USA', '73301', '1991-09-14'),
        ('Henry', 'Anderson', 'henry.anderson@email.com', '+1-555-0208', '258 Spruce Ct, Nashville, TN', 'Nashville', 'TN', 'USA', '37201', '1987-04-25')
    ]
    
    for first_name, last_name, email, phone, address, city, state, country, postal_code, dob in customers_data:
        connection.execute(text("""
            INSERT INTO customers (first_name, last_name, email, phone, address, city, state, country, postal_code, date_of_birth)
            VALUES (:first_name, :last_name, :email, :phone, :address, :city, :state, :country, :postal_code, :dob)
            ON CONFLICT DO NOTHING
        """), {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone, "address": address, "city": city, "state": state, "country": country, "postal_code": postal_code, "dob": dob})
    
    # Insert products
    products_data = [
        ('MacBook Pro 16"', 'Latest MacBook Pro with M2 chip, 16GB RAM, 512GB SSD', 'MBP16-M2-512', 2, 1, 2499.99, 1800.00, 2.1, '35.8x24.8x1.7'),
        ('iPhone 15 Pro', 'Apple iPhone 15 Pro with A17 Pro chip, 128GB storage', 'IPH15-PRO-128', 3, 1, 999.99, 650.00, 0.187, '14.7x7.1x0.8'),
        ('Samsung Galaxy S24', 'Samsung Galaxy S24 with Snapdragon 8 Gen 3, 256GB', 'SAMS24-256', 3, 2, 899.99, 600.00, 0.168, '14.7x7.0x0.8'),
        ('Dell XPS 13', 'Dell XPS 13 laptop with Intel i7, 16GB RAM, 512GB SSD', 'DELL-XPS13-512', 2, 2, 1299.99, 900.00, 1.2, '30.2x19.9x1.4'),
        ('Wireless Mouse', 'Ergonomic wireless mouse with precision tracking', 'MOUSE-WL-001', 4, 1, 49.99, 25.00, 0.1, '12.5x6.8x3.9'),
        ('Mechanical Keyboard', 'RGB mechanical keyboard with Cherry MX switches', 'KB-MECH-RGB', 4, 1, 129.99, 70.00, 0.9, '44.5x13.8x3.5'),
        ('4K Monitor', '27-inch 4K monitor with HDR support', 'MON-27-4K', 4, 2, 399.99, 250.00, 5.8, '61.1x36.6x5.5'),
        ('Men\'s Casual Shirt', 'Cotton casual shirt for men, various colors', 'SHIRT-M-CAS', 6, 3, 29.99, 15.00, 0.3, '30x20x2'),
        ('Women\'s Dress', 'Elegant evening dress, perfect for special occasions', 'DRESS-W-EVE', 7, 3, 89.99, 45.00, 0.4, '35x25x3'),
        ('Coffee Table', 'Modern wooden coffee table with storage', 'TABLE-COFFEE', 9, 4, 299.99, 180.00, 25.0, '120x60x45'),
        ('Garden Chair', 'Comfortable outdoor garden chair, weather resistant', 'CHAIR-GARDEN', 8, 4, 79.99, 40.00, 3.2, '85x55x90'),
        ('Python Programming Book', 'Complete guide to Python programming language', 'BOOK-PYTHON', 11, 5, 39.99, 20.00, 0.8, '23.5x19.1x2.5'),
        ('Data Science Handbook', 'Comprehensive data science and machine learning guide', 'BOOK-DATA', 12, 5, 49.99, 25.00, 1.1, '25.4x20.3x3.2')
    ]
    
    for name, description, sku, category_id, supplier_id, price, cost_price, weight, dimensions in products_data:
        connection.execute(text("""
            INSERT INTO products (name, description, sku, category_id, supplier_id, price, cost_price, weight_kg, dimensions_cm)
            VALUES (:name, :description, :sku, :category_id, :supplier_id, :price, :cost_price, :weight, :dimensions)
            ON CONFLICT DO NOTHING
        """), {"name": name, "description": description, "sku": sku, "category_id": category_id, "supplier_id": supplier_id, "price": price, "cost_price": cost_price, "weight": weight, "dimensions": dimensions})
    
    # Insert inventory
    inventory_data = [
        (1, 'Warehouse A - Section 1', 45, 10, 100),
        (2, 'Warehouse A - Section 2', 120, 20, 200),
        (3, 'Warehouse A - Section 2', 85, 15, 150),
        (4, 'Warehouse B - Section 1', 30, 8, 80),
        (5, 'Warehouse A - Section 3', 200, 25, 300),
        (6, 'Warehouse A - Section 3', 75, 15, 120),
        (7, 'Warehouse B - Section 2', 40, 10, 80),
        (8, 'Warehouse C - Section 1', 150, 30, 200),
        (9, 'Warehouse C - Section 1', 80, 20, 150),
        (10, 'Warehouse B - Section 3', 25, 5, 50),
        (11, 'Warehouse C - Section 2', 60, 10, 100),
        (12, 'Warehouse A - Section 4', 90, 20, 150),
        (13, 'Warehouse A - Section 4', 70, 15, 120)
    ]
    
    for product_id, location, quantity, reorder_level, max_level in inventory_data:
        connection.execute(text("""
            INSERT INTO inventory (product_id, warehouse_location, quantity_in_stock, reorder_level, max_stock_level)
            VALUES (:product_id, :location, :quantity, :reorder_level, :max_level)
            ON CONFLICT DO NOTHING
        """), {"product_id": product_id, "location": location, "quantity": quantity, "reorder_level": reorder_level, "max_level": max_level})
    
    # Insert shipping methods
    shipping_methods = [
        ('Standard Shipping', '5-7 business days', 9.99, 7),
        ('Express Shipping', '2-3 business days', 19.99, 3),
        ('Overnight Shipping', 'Next business day', 29.99, 1),
        ('Free Shipping', '7-10 business days (orders over $50)', 0.00, 10)
    ]
    
    for name, description, cost, delivery_days in shipping_methods:
        connection.execute(text("""
            INSERT INTO shipping_methods (name, description, base_cost, delivery_time_days)
            VALUES (:name, :description, :cost, :delivery_days)
            ON CONFLICT DO NOTHING
        """), {"name": name, "description": description, "cost": cost, "delivery_days": delivery_days})
    
    # Insert orders and order items
    create_sample_orders(connection)
    
    # Insert product reviews
    create_sample_reviews(connection)

def create_sample_orders(connection):
    # Create orders for the last 6 months
    base_date = datetime.now() - timedelta(days=180)
    
    orders_data = [
        (1, base_date + timedelta(days=5), 'completed', 2549.98, '123 Main St, Boston, MA', '123 Main St, Boston, MA', 'credit_card', 'paid', 19.99, 0.0, 0.0),
        (2, base_date + timedelta(days=12), 'completed', 899.99, '456 Oak Ave, San Francisco, CA', '456 Oak Ave, San Francisco, CA', 'paypal', 'paid', 9.99, 0.0, 0.0),
        (3, base_date + timedelta(days=18), 'completed', 179.97, '789 Pine Rd, Miami, FL', '789 Pine Rd, Miami, FL', 'credit_card', 'paid', 0.0, 0.0, 0.0),
        (4, base_date + timedelta(days=25), 'shipped', 1299.99, '321 Elm St, Seattle, WA', '321 Elm St, Seattle, WA', 'credit_card', 'paid', 19.99, 0.0, 0.0),
        (5, base_date + timedelta(days=32), 'completed', 89.99, '654 Maple Dr, Denver, CO', '654 Maple Dr, Denver, CO', 'paypal', 'paid', 9.99, 0.0, 0.0),
        (1, base_date + timedelta(days=40), 'completed', 399.99, '123 Main St, Boston, MA', '123 Main St, Boston, MA', 'credit_card', 'paid', 0.0, 0.0, 0.0),
        (6, base_date + timedelta(days=47), 'pending', 79.99, '987 Cedar Ln, Portland, OR', '987 Cedar Ln, Portland, OR', 'credit_card', 'pending', 9.99, 0.0, 0.0),
        (7, base_date + timedelta(days=55), 'completed', 49.98, '147 Birch Way, Austin, TX', '147 Birch Way, Austin, TX', 'paypal', 'paid', 0.0, 0.0, 0.0),
        (8, base_date + timedelta(days=62), 'completed', 379.98, '258 Spruce Ct, Nashville, TN', '258 Spruce Ct, Nashville, TN', 'credit_card', 'paid', 19.99, 0.0, 0.0),
        (2, base_date + timedelta(days=70), 'completed', 129.99, '456 Oak Ave, San Francisco, CA', '456 Oak Ave, San Francisco, CA', 'credit_card', 'paid', 9.99, 0.0, 0.0),
        (3, base_date + timedelta(days=78), 'shipped', 299.99, '789 Pine Rd, Miami, FL', '789 Pine Rd, Miami, FL', 'paypal', 'paid', 19.99, 0.0, 0.0),
        (4, base_date + timedelta(days=85), 'completed', 89.98, '321 Elm St, Seattle, WA', '321 Elm St, Seattle, WA', 'credit_card', 'paid', 0.0, 0.0, 0.0),
        (5, base_date + timedelta(days=92), 'pending', 159.98, '654 Maple Dr, Denver, CO', '654 Maple Dr, Denver, CO', 'paypal', 'pending', 9.99, 0.0, 0.0),
        (6, base_date + timedelta(days=100), 'completed', 39.99, '987 Cedar Ln, Portland, OR', '987 Cedar Ln, Portland, OR', 'credit_card', 'paid', 0.0, 0.0, 0.0),
        (7, base_date + timedelta(days=108), 'completed', 49.99, '147 Birch Way, Austin, TX', '147 Birch Way, Austin, TX', 'paypal', 'paid', 9.99, 0.0, 0.0)
    ]
    
    for customer_id, order_date, status, total_amount, shipping_addr, billing_addr, payment_method, payment_status, shipping_cost, tax, discount in orders_data:
        connection.execute(text("""
            INSERT INTO orders (customer_id, order_date, status, total_amount, shipping_address, billing_address, payment_method, payment_status, shipping_cost, tax_amount, discount_amount)
            VALUES (:customer_id, :order_date, :status, :total_amount, :shipping_addr, :billing_addr, :payment_method, :payment_status, :shipping_cost, :tax, :discount)
            ON CONFLICT DO NOTHING
        """), {"customer_id": customer_id, "order_date": order_date, "status": status, "total_amount": total_amount, "shipping_addr": shipping_addr, "billing_addr": billing_addr, "payment_method": payment_method, "payment_status": payment_status, "shipping_cost": shipping_cost, "tax": tax, "discount": discount})
    
    # Insert order items
    order_items_data = [
        (1, 1, 1, 2499.99, 2499.99, 0.0),  # MacBook Pro
        (1, 5, 1, 49.99, 49.99, 0.0),      # Mouse
        (2, 3, 1, 899.99, 899.99, 0.0),    # Samsung Galaxy
        (3, 5, 2, 49.99, 99.98, 0.0),      # 2 Mice
        (3, 6, 1, 129.99, 129.99, 0.0),    # Keyboard
        (4, 4, 1, 1299.99, 1299.99, 0.0),  # Dell XPS
        (5, 9, 1, 89.99, 89.99, 0.0),      # Dress
        (6, 7, 1, 399.99, 399.99, 0.0),    # Monitor
        (7, 11, 1, 79.99, 79.99, 0.0),     # Garden Chair
        (8, 5, 1, 49.99, 49.99, 0.0),      # Mouse
        (8, 6, 1, 129.99, 129.99, 0.0),    # Keyboard
        (8, 7, 1, 399.99, 399.99, 0.0),    # Monitor
        (9, 2, 1, 899.99, 899.99, 0.0),    # iPhone
        (10, 6, 1, 129.99, 129.99, 0.0),   # Keyboard
        (11, 7, 1, 399.99, 399.99, 0.0),   # Monitor
        (12, 8, 1, 29.99, 29.99, 0.0),     # Men's Shirt
        (12, 9, 1, 89.99, 89.99, 0.0),     # Women's Dress
        (13, 6, 1, 129.99, 129.99, 0.0),   # Keyboard
        (13, 5, 1, 29.99, 29.99, 0.0),     # Mouse
        (14, 12, 1, 39.99, 39.99, 0.0),    # Python Book
        (15, 13, 1, 49.99, 49.99, 0.0),    # Data Science Book
    ]
    
    for order_id, product_id, quantity, unit_price, total_price, discount in order_items_data:
        connection.execute(text("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price, discount_percentage)
            VALUES (:order_id, :product_id, :quantity, :unit_price, :total_price, :discount)
            ON CONFLICT DO NOTHING
        """), {"order_id": order_id, "product_id": product_id, "quantity": quantity, "unit_price": unit_price, "total_price": total_price, "discount": discount})

def create_sample_reviews(connection):
    reviews_data = [
        (1, 1, 5, 'Excellent laptop! The M2 chip is incredibly fast and the battery life is amazing.', True),
        (1, 5, 4, 'Good wireless mouse, comfortable to use for long hours.', True),
        (2, 3, 5, 'Great phone with excellent camera quality and performance.', True),
        (3, 5, 3, 'Decent mouse but could be more ergonomic.', True),
        (3, 6, 5, 'Love this mechanical keyboard! The RGB lighting is beautiful.', True),
        (4, 4, 4, 'Solid laptop, good performance for the price.', True),
        (5, 9, 5, 'Beautiful dress, perfect fit and great quality material.', True),
        (6, 7, 4, 'Good monitor with crisp 4K resolution.', True),
        (7, 11, 3, 'Comfortable chair but could be more durable.', True),
        (8, 5, 4, 'Reliable wireless mouse, good battery life.', True),
        (8, 6, 5, 'Excellent keyboard with great tactile feedback.', True),
        (8, 7, 5, 'Outstanding monitor, colors are vibrant and accurate.', True),
        (9, 2, 5, 'Amazing iPhone! The camera and performance are top-notch.', True),
        (10, 6, 4, 'Good mechanical keyboard, switches feel great.', True),
        (11, 7, 4, 'Nice 4K monitor, good for both work and gaming.', True),
        (12, 8, 3, 'Decent shirt but the fabric could be better quality.', True),
        (12, 9, 5, 'Stunning dress, received many compliments!', True),
        (13, 6, 4, 'Solid keyboard, good build quality.', True),
        (13, 5, 3, 'Basic mouse, works fine but nothing special.', True),
        (14, 12, 5, 'Excellent book for learning Python! Very comprehensive.', True),
        (15, 13, 5, 'Great resource for data science concepts and techniques.', True)
    ]
    
    for product_id, customer_id, rating, review_text, verified in reviews_data:
        connection.execute(text("""
            INSERT INTO product_reviews (product_id, customer_id, rating, review_text, is_verified_purchase)
            VALUES (:product_id, :customer_id, :rating, :review_text, :verified)
            ON CONFLICT DO NOTHING
        """), {"product_id": product_id, "customer_id": customer_id, "rating": rating, "review_text": review_text, "verified": verified})

if __name__ == "__main__":
    init_db()
    print("Database initialized with complex data structure and sample data!") 