"""
Test Generator Module
Generates unit tests for modernized services
"""

import os


class TestGenerator:
    """Generates unit tests for microservices"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
    
    def generate_all_tests(self) -> None:
        """Generate tests for all services"""
        self._generate_user_service_tests()
        self._generate_product_service_tests()
        self._generate_order_service_tests()
        self._generate_payment_service_tests()
    
    def _generate_user_service_tests(self) -> None:
        """Generate tests for User Service"""
        
        test_code = '''"""
Unit tests for User Service
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from userservice.main import app, get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_user():
    """Test registering duplicate user"""
    # First registration
    client.post(
        "/register",
        json={
            "username": "duplicate",
            "password": "pass123",
            "email": "dup@example.com"
        }
    )
    
    # Duplicate registration
    response = client.post(
        "/register",
        json={
            "username": "duplicate",
            "password": "pass123",
            "email": "dup2@example.com"
        }
    )
    assert response.status_code == 400


def test_login_user():
    """Test user login"""
    # Register user first
    client.post(
        "/register",
        json={
            "username": "logintest",
            "password": "loginpass",
            "email": "login@example.com"
        }
    )
    
    # Login
    response = client.post(
        "/login",
        json={
            "username": "logintest",
            "password": "loginpass"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "user_id" in data


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/login",
        json={
            "username": "nonexistent",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "user-service"


# Cleanup
def teardown_module(module):
    """Clean up test database"""
    os.remove("./test_users.db")
'''
        
        test_dir = f"{self.output_dir}/services/userservice"
        with open(f"{test_dir}/test_main.py", 'w') as f:
            f.write(test_code)
    
    def _generate_product_service_tests(self) -> None:
        """Generate tests for Product Service"""
        
        test_code = '''"""
Unit tests for Product Service
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from productservice.main import app, get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_products.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_product():
    """Test product creation"""
    response = client.post(
        "/products",
        json={
            "name": "Test Laptop",
            "price": 999.99,
            "stock": 10
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Laptop"
    assert data["price"] == 999.99
    assert data["stock"] == 10


def test_get_all_products():
    """Test getting all products"""
    # Create a product first
    client.post(
        "/products",
        json={
            "name": "Mouse",
            "price": 29.99,
            "stock": 50
        }
    )
    
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_product_by_id():
    """Test getting product by ID"""
    # Create a product
    create_response = client.post(
        "/products",
        json={
            "name": "Keyboard",
            "price": 79.99,
            "stock": 25
        }
    )
    product_id = create_response.json()["id"]
    
    # Get the product
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Keyboard"


def test_update_stock():
    """Test stock update"""
    # Create a product
    create_response = client.post(
        "/products",
        json={
            "name": "Monitor",
            "price": 299.99,
            "stock": 15
        }
    )
    product_id = create_response.json()["id"]
    
    # Update stock
    response = client.patch(
        f"/products/{product_id}/stock",
        params={"quantity": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["new_stock"] == 20


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# Cleanup
def teardown_module(module):
    """Clean up test database"""
    os.remove("./test_products.db")
'''
        
        test_dir = f"{self.output_dir}/services/productservice"
        with open(f"{test_dir}/test_main.py", 'w') as f:
            f.write(test_code)
    
    def _generate_order_service_tests(self) -> None:
        """Generate tests for Order Service"""
        
        test_code = '''"""
Unit tests for Order Service
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orderservice.main import app, get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_orders.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "order-service"


# Note: Full integration tests would require mocking the user and product services
# or running them in a test environment


# Cleanup
def teardown_module(module):
    """Clean up test database"""
    if os.path.exists("./test_orders.db"):
        os.remove("./test_orders.db")
'''
        
        test_dir = f"{self.output_dir}/services/orderservice"
        with open(f"{test_dir}/test_main.py", 'w') as f:
            f.write(test_code)
    
    def _generate_payment_service_tests(self) -> None:
        """Generate tests for Payment Service"""
        
        test_code = '''"""
Unit tests for Payment Service
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paymentservice.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "payment-service"


# Note: Full integration tests would require mocking the order service
# or running it in a test environment
'''
        
        test_dir = f"{self.output_dir}/services/paymentservice"
        with open(f"{test_dir}/test_main.py", 'w') as f:
            f.write(test_code)
    
    def generate_pytest_config(self) -> None:
        """Generate pytest configuration"""
        
        pytest_ini = '''[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
'''
        
        with open(f"{self.output_dir}/pytest.ini", 'w') as f:
            f.write(pytest_ini)
        
        # Generate test requirements
        test_requirements = '''pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
'''
        
        with open(f"{self.output_dir}/test_requirements.txt", 'w') as f:
            f.write(test_requirements)

# Made with Bob
