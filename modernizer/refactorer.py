"""
Code Refactoring Module
Transforms legacy monolithic code into modern microservices
"""

import os
from typing import Dict, List
from modernizer.analyzer import AnalysisResult, CodeModule


class CodeRefactorer:
    """Refactors legacy code into modern microservices"""
    
    def __init__(self, analysis_result: AnalysisResult):
        self.analysis = analysis_result
        self.output_dir = "output"
    
    def generate_microservices(self) -> None:
        """Generate all microservices from analysis"""
        
        # Generate database models
        self._generate_database_models()
        
        # Generate each service
        for module_name, module in self.analysis.modules.items():
            self._generate_service(module_name, module)
        
        # Generate API gateway
        self._generate_api_gateway()
    
    def _generate_database_models(self) -> None:
        """Generate database models using SQLAlchemy"""
        models_code = '''"""
Database Models
SQLAlchemy ORM models for the application
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Product(Base):
    """Product model"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Order(Base):
    """Order model"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    product = relationship("Product")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
'''
        
        os.makedirs(f"{self.output_dir}/services/shared", exist_ok=True)
        with open(f"{self.output_dir}/services/shared/models.py", 'w') as f:
            f.write(models_code)
    
    def _generate_service(self, service_name: str, module: CodeModule) -> None:
        """Generate a microservice"""
        
        service_dir = f"{self.output_dir}/services/{service_name.lower()}"
        os.makedirs(service_dir, exist_ok=True)
        
        # Generate service logic
        if service_name == "UserService":
            self._generate_user_service(service_dir)
        elif service_name == "ProductService":
            self._generate_product_service(service_dir)
        elif service_name == "OrderService":
            self._generate_order_service(service_dir)
        elif service_name == "PaymentService":
            self._generate_payment_service(service_dir)
        elif service_name == "ReportingService":
            self._generate_reporting_service(service_dir)
    
    def _generate_user_service(self, service_dir: str) -> None:
        """Generate User Service"""
        
        service_code = '''"""
User Service
Handles user authentication and management
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.models import Base, User

app = FastAPI(title="User Service", version="1.0.0")

# Database setup
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoints
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        password=hashed_password,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.post("/login")
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not pwd_context.verify(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username
    }


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
'''
        
        with open(f"{service_dir}/main.py", 'w') as f:
            f.write(service_code)
        
        # Generate requirements
        requirements = '''fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
passlib==1.7.4
bcrypt==4.1.1
python-multipart==0.0.6
'''
        with open(f"{service_dir}/requirements.txt", 'w') as f:
            f.write(requirements)
    
    def _generate_product_service(self, service_dir: str) -> None:
        """Generate Product Service"""
        
        service_code = '''"""
Product Service
Handles product catalog and inventory management
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.models import Base, Product

app = FastAPI(title="Product Service", version="1.0.0")

# Database setup
DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# Pydantic models
class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int


class ProductUpdate(BaseModel):
    name: str = None
    price: float = None
    stock: int = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    
    class Config:
        from_attributes = True


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoints
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Get all products"""
    products = db.query(Product).all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Update product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@app.patch("/products/{product_id}/stock")
def update_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
    """Update product stock"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.stock += quantity
    if product.stock < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    db.commit()
    db.refresh(product)
    return {"message": "Stock updated", "new_stock": product.stock}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "product-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
'''
        
        with open(f"{service_dir}/main.py", 'w') as f:
            f.write(service_code)
        
        requirements = '''fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
'''
        with open(f"{service_dir}/requirements.txt", 'w') as f:
            f.write(requirements)
    
    def _generate_order_service(self, service_dir: str) -> None:
        """Generate Order Service"""
        
        service_code = '''"""
Order Service
Handles order processing and management
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.models import Base, Order

app = FastAPI(title="Order Service", version="1.0.0")

# Database setup
DATABASE_URL = "sqlite:///./orders.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Service URLs
PRODUCT_SERVICE_URL = "http://localhost:8002"
USER_SERVICE_URL = "http://localhost:8001"


# Pydantic models
class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total: float
    status: str
    
    class Config:
        from_attributes = True


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoints
@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    
    # Verify user exists
    async with httpx.AsyncClient() as client:
        try:
            user_response = await client.get(f"{USER_SERVICE_URL}/users/{order.user_id}")
            if user_response.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User service unavailable")
        
        # Get product details
        try:
            product_response = await client.get(f"{PRODUCT_SERVICE_URL}/products/{order.product_id}")
            if product_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Product not found")
            
            product = product_response.json()
            
            # Check stock
            if product['stock'] < order.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            
            # Calculate total
            total = product['price'] * order.quantity
            
            # Create order
            db_order = Order(
                user_id=order.user_id,
                product_id=order.product_id,
                quantity=order.quantity,
                total=total,
                status='pending'
            )
            db.add(db_order)
            db.commit()
            db.refresh(db_order)
            
            # Update stock
            await client.patch(
                f"{PRODUCT_SERVICE_URL}/products/{order.product_id}/stock",
                params={"quantity": -order.quantity}
            )
            
            return db_order
            
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Product service unavailable")


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/orders/user/{user_id}", response_model=List[OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """Get all orders for a user"""
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return orders


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "order-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
'''
        
        with open(f"{service_dir}/main.py", 'w') as f:
            f.write(service_code)
        
        requirements = '''fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
httpx==0.25.2
'''
        with open(f"{service_dir}/requirements.txt", 'w') as f:
            f.write(requirements)
    
    def _generate_payment_service(self, service_dir: str) -> None:
        """Generate Payment Service"""
        
        service_code = '''"""
Payment Service
Handles payment processing
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
import httpx

app = FastAPI(title="Payment Service", version="1.0.0")

ORDER_SERVICE_URL = "http://localhost:8003"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class PaymentRequest(BaseModel):
    order_id: int
    payment_method: PaymentMethod
    amount: float


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    message: str


@app.post("/payments", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest):
    """Process a payment"""
    
    # Verify order exists
    async with httpx.AsyncClient() as client:
        try:
            order_response = await client.get(f"{ORDER_SERVICE_URL}/orders/{payment.order_id}")
            if order_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Order not found")
            
            order = order_response.json()
            
            # Verify amount matches
            if abs(order['total'] - payment.amount) > 0.01:
                raise HTTPException(status_code=400, detail="Payment amount mismatch")
            
            # Simulate payment processing
            transaction_id = f"TXN-{payment.order_id}-{payment.payment_method.value}"
            
            return PaymentResponse(
                transaction_id=transaction_id,
                status="success",
                message=f"Payment processed successfully via {payment.payment_method.value}"
            )
            
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Order service unavailable")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "payment-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
'''
        
        with open(f"{service_dir}/main.py", 'w') as f:
            f.write(service_code)
        
        requirements = '''fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
httpx==0.25.2
'''
        with open(f"{service_dir}/requirements.txt", 'w') as f:
            f.write(requirements)
    
    def _generate_reporting_service(self, service_dir: str) -> None:
        """Generate Reporting Service"""
        
        service_code = '''"""
Reporting Service
Handles analytics and reporting
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import httpx

app = FastAPI(title="Reporting Service", version="1.0.0")

ORDER_SERVICE_URL = "http://localhost:8003"
PRODUCT_SERVICE_URL = "http://localhost:8002"


class SalesReport(BaseModel):
    total_orders: int
    total_revenue: float
    average_order_value: float


@app.get("/reports/sales", response_model=SalesReport)
async def get_sales_report():
    """Generate sales report"""
    
    async with httpx.AsyncClient() as client:
        try:
            # This is a simplified version - in production, you'd query a data warehouse
            # For now, we'll return mock data
            return SalesReport(
                total_orders=100,
                total_revenue=50000.00,
                average_order_value=500.00
            )
            
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/reports/inventory")
async def get_inventory_report():
    """Generate inventory report"""
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PRODUCT_SERVICE_URL}/products")
            if response.status_code != 200:
                raise HTTPException(status_code=503, detail="Product service unavailable")
            
            products = response.json()
            
            total_products = len(products)
            total_stock = sum(p['stock'] for p in products)
            low_stock_items = [p for p in products if p['stock'] < 10]
            
            return {
                "total_products": total_products,
                "total_stock": total_stock,
                "low_stock_count": len(low_stock_items),
                "low_stock_items": low_stock_items
            }
            
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Product service unavailable")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "reporting-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
'''
        
        with open(f"{service_dir}/main.py", 'w') as f:
            f.write(service_code)
        
        requirements = '''fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
httpx==0.25.2
'''
        with open(f"{service_dir}/requirements.txt", 'w') as f:
            f.write(requirements)
    
    def _generate_api_gateway(self) -> None:
        """Generate API Gateway"""
        
        gateway_code = '''"""
API Gateway
Routes requests to appropriate microservices
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "user": "http://localhost:8001",
    "product": "http://localhost:8002",
    "order": "http://localhost:8003",
    "payment": "http://localhost:8004",
    "reporting": "http://localhost:8005"
}


@app.get("/")
def root():
    """API Gateway root"""
    return {
        "message": "API Gateway",
        "version": "1.0.0",
        "services": list(SERVICES.keys())
    }


@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request):
    """Route requests to appropriate service"""
    
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    service_url = f"{SERVICES[service]}/{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request
            response = await client.request(
                method=request.method,
                url=service_url,
                params=request.query_params,
                json=await request.json() if request.method in ["POST", "PUT", "PATCH"] else None
            )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/health")
async def health_check():
    """Check health of all services"""
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=2.0)
                health_status[service_name] = response.json()
            except:
                health_status[service_name] = {"status": "unhealthy"}
    
    return {
        "gateway": "healthy",
        "services": health_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        os.makedirs(f"{self.output_dir}/api/routes", exist_ok=True)
        with open(f"{self.output_dir}/api/gateway.py", 'w') as f:
            f.write(gateway_code)
        
        requirements = '''fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
'''
        with open(f"{self.output_dir}/api/requirements.txt", 'w') as f:
            f.write(requirements)

# Made with Bob
