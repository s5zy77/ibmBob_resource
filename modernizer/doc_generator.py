"""
Documentation Generator Module
Generates comprehensive documentation for the modernization process
"""

import os
from typing import Dict, List
from modernizer.analyzer import AnalysisResult


class DocumentationGenerator:
    """Generates documentation for modernized codebase"""
    
    def __init__(self, analysis_result: AnalysisResult, output_dir: str = "output"):
        self.analysis = analysis_result
        self.output_dir = output_dir
    
    def generate_all_docs(self) -> None:
        """Generate all documentation"""
        self._generate_modernization_roadmap()
        self._generate_dependency_map()
        self._generate_main_readme()
        self._generate_architecture_doc()
        self._generate_api_documentation()
    
    def _generate_modernization_roadmap(self) -> None:
        """Generate modernization roadmap document"""
        
        roadmap = self.analysis.generate_modernization_roadmap()
        
        content = """# Modernization Roadmap

This document outlines the step-by-step process for modernizing the legacy monolithic application into a microservices architecture.

## Overview

The legacy application has been analyzed and identified as a tightly-coupled monolithic system with the following issues:
- Global state management
- Mixed responsibilities in a single class
- No separation of concerns
- Weak security practices
- Poor scalability

## Modernization Steps

"""
        
        for step in roadmap:
            content += f"""### Step {step['step']}: {step['title']}

**Priority:** {step['priority']}  
**Effort:** {step['effort']}

**Description:** {step['description']}

---

"""
        
        content += """## Expected Benefits

1. **Scalability**: Each service can be scaled independently based on demand
2. **Maintainability**: Smaller, focused codebases are easier to understand and modify
3. **Reliability**: Failures in one service don't bring down the entire system
4. **Technology Flexibility**: Different services can use different technologies
5. **Team Autonomy**: Different teams can work on different services independently
6. **Deployment Flexibility**: Services can be deployed independently

## Timeline Estimate

- **Phase 1** (Steps 1-3): 2-3 weeks
- **Phase 2** (Steps 4-6): 3-4 weeks
- **Phase 3** (Steps 7-10): 2-3 weeks

**Total Estimated Time:** 7-10 weeks

## Success Metrics

- All services running independently
- API response times < 200ms
- 99.9% uptime for critical services
- Zero data loss during migration
- All tests passing with >80% coverage
"""
        
        os.makedirs(f"{self.output_dir}/docs", exist_ok=True)
        with open(f"{self.output_dir}/docs/modernization_roadmap.md", 'w') as f:
            f.write(content)
    
    def _generate_dependency_map(self) -> None:
        """Generate dependency map document"""
        
        dependencies = self.analysis.identify_dependencies()
        
        content = """# Dependency Map

This document maps the dependencies between microservices in the modernized architecture.

## Service Dependencies

"""
        
        # List all services
        content += "### Services Overview\n\n"
        for module_name in self.analysis.modules.keys():
            content += f"- **{module_name}**: {', '.join(self.analysis.modules[module_name].responsibilities)}\n"
        
        content += "\n## Dependency Graph\n\n"
        content += "```\n"
        content += "┌─────────────────┐\n"
        content += "│   API Gateway   │\n"
        content += "└────────┬────────┘\n"
        content += "         │\n"
        content += "    ┌────┴────┬────────┬──────────┬──────────┐\n"
        content += "    │         │        │          │          │\n"
        content += "┌───▼───┐ ┌──▼───┐ ┌──▼────┐ ┌───▼────┐ ┌──▼────┐\n"
        content += "│ User  │ │Product│ │ Order │ │Payment │ │Report │\n"
        content += "│Service│ │Service│ │Service│ │Service │ │Service│\n"
        content += "└───────┘ └───────┘ └───┬───┘ └───┬────┘ └───┬───┘\n"
        content += "                        │         │          │\n"
        content += "                        └─────────┴──────────┘\n"
        content += "                        (depends on other services)\n"
        content += "```\n\n"
        
        content += "## Detailed Dependencies\n\n"
        
        for service, deps in dependencies.items():
            content += f"### {service}\n\n"
            if deps:
                content += "**Depends on:**\n"
                for dep in deps:
                    content += f"- {dep}\n"
            else:
                content += "**No dependencies** (independent service)\n"
            content += "\n"
        
        content += """## Communication Patterns

### Synchronous Communication (HTTP/REST)
- Used for real-time operations
- Order Service → Product Service (check stock)
- Order Service → User Service (verify user)
- Payment Service → Order Service (verify order)

### Asynchronous Communication (Future Enhancement)
- Event-driven architecture using message queues
- Order created → Inventory updated
- Payment processed → Order status updated

## Database Strategy

### Current: Database per Service
Each service has its own database:
- `users.db` - User Service
- `products.db` - Product Service
- `orders.db` - Order Service

### Benefits:
- Service independence
- Technology flexibility
- Easier scaling

### Challenges:
- Data consistency (eventual consistency)
- Complex queries across services
- Data duplication

## API Contracts

All services expose RESTful APIs with:
- JSON request/response format
- Standard HTTP status codes
- Consistent error handling
- Health check endpoints
"""
        
        with open(f"{self.output_dir}/docs/dependency_map.md", 'w') as f:
            f.write(content)
    
    def _generate_main_readme(self) -> None:
        """Generate main README"""
        
        content = """# Modernized E-Commerce Microservices

This project is the result of modernizing a legacy monolithic e-commerce application into a microservices architecture.

## 🎯 What Was Done

### Legacy Code Issues Identified
- ❌ Monolithic architecture with all logic in one file
- ❌ Global state management (global variables)
- ❌ Tightly coupled components
- ❌ No separation of concerns
- ❌ Weak security (MD5 password hashing)
- ❌ Poor scalability
- ❌ Difficult to test and maintain

### Modernization Transformations
- ✅ Separated into 5 independent microservices
- ✅ Each service has its own database
- ✅ RESTful API design
- ✅ Modern security (bcrypt password hashing)
- ✅ Dependency injection
- ✅ API Gateway for routing
- ✅ Health check endpoints
- ✅ Comprehensive documentation
- ✅ Unit tests for each service

## 🏗️ Architecture

### Microservices

1. **User Service** (Port 8001)
   - User registration and authentication
   - Password hashing with bcrypt
   - User profile management

2. **Product Service** (Port 8002)
   - Product catalog management
   - Inventory tracking
   - Stock updates

3. **Order Service** (Port 8003)
   - Order creation and management
   - Coordinates with User and Product services
   - Order history

4. **Payment Service** (Port 8004)
   - Payment processing
   - Transaction management
   - Multiple payment methods

5. **Reporting Service** (Port 8005)
   - Sales analytics
   - Inventory reports
   - Business intelligence

6. **API Gateway** (Port 8000)
   - Single entry point for all services
   - Request routing
   - Service health monitoring

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Install dependencies for each service:

```bash
# User Service
cd services/userservice
pip install -r requirements.txt

# Product Service
cd ../productservice
pip install -r requirements.txt

# Order Service
cd ../orderservice
pip install -r requirements.txt

# Payment Service
cd ../paymentservice
pip install -r requirements.txt

# Reporting Service
cd ../reportingservice
pip install -r requirements.txt

# API Gateway
cd ../../api
pip install -r requirements.txt
```

### Running the Services

Start each service in a separate terminal:

```bash
# Terminal 1 - User Service
cd services/userservice
python main.py

# Terminal 2 - Product Service
cd services/productservice
python main.py

# Terminal 3 - Order Service
cd services/orderservice
python main.py

# Terminal 4 - Payment Service
cd services/paymentservice
python main.py

# Terminal 5 - Reporting Service
cd services/reportingservice
python main.py

# Terminal 6 - API Gateway
cd api
python gateway.py
```

### Using the API

Once all services are running, access the API through the gateway at `http://localhost:8000`

#### Example Requests

**Register a User:**
```bash
curl -X POST http://localhost:8000/user/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "john_doe",
    "password": "secure_password",
    "email": "john@example.com"
  }'
```

**Create a Product:**
```bash
curl -X POST http://localhost:8000/product/products \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Laptop",
    "price": 999.99,
    "stock": 10
  }'
```

**Get All Products:**
```bash
curl http://localhost:8000/product/products
```

**Create an Order:**
```bash
curl -X POST http://localhost:8000/order/orders \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_id": 1,
    "product_id": 1,
    "quantity": 2
  }'
```

## 📊 API Documentation

Each service provides interactive API documentation:

- User Service: http://localhost:8001/docs
- Product Service: http://localhost:8002/docs
- Order Service: http://localhost:8003/docs
- Payment Service: http://localhost:8004/docs
- Reporting Service: http://localhost:8005/docs
- API Gateway: http://localhost:8000/docs

## 🧪 Testing

Run tests for all services:

```bash
# Install test dependencies
pip install -r test_requirements.txt

# Run all tests
pytest

# Run tests for specific service
pytest services/userservice/test_main.py -v
```

## 📁 Project Structure

```
output/
├── services/
│   ├── shared/
│   │   └── models.py          # Shared database models
│   ├── userservice/
│   │   ├── main.py            # User service implementation
│   │   ├── requirements.txt
│   │   └── test_main.py       # Unit tests
│   ├── productservice/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── test_main.py
│   ├── orderservice/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── test_main.py
│   ├── paymentservice/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── test_main.py
│   └── reportingservice/
│       ├── main.py
│       ├── requirements.txt
│       └── test_main.py
├── api/
│   ├── gateway.py             # API Gateway
│   └── requirements.txt
└── docs/
    ├── modernization_roadmap.md
    ├── dependency_map.md
    └── architecture.md
```

## 🔒 Security Improvements

- **Password Hashing**: Upgraded from MD5 to bcrypt
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: SQLAlchemy ORM
- **CORS Configuration**: Proper CORS middleware in API Gateway

## 📈 Performance & Scalability

- Each service can be scaled independently
- Horizontal scaling supported
- Database per service pattern
- Stateless services for easy replication

## 🔄 Future Enhancements

- [ ] Add authentication tokens (JWT)
- [ ] Implement service discovery
- [ ] Add message queue for async communication
- [ ] Containerize with Docker
- [ ] Add Kubernetes orchestration
- [ ] Implement circuit breakers
- [ ] Add distributed tracing
- [ ] Implement caching layer

## 📝 License

This is a Proof of Concept for educational purposes.

## 🤝 Contributing

This is a demonstration project showing legacy code modernization techniques.

---

**Transformation Complete!** 🎉

From a 145-line monolithic mess to a clean, scalable microservices architecture.
"""
        
        with open(f"{self.output_dir}/README.md", 'w') as f:
            f.write(content)
    
    def _generate_architecture_doc(self) -> None:
        """Generate architecture documentation"""
        
        content = """# Architecture Documentation

## System Architecture

### High-Level Overview

The modernized system follows a microservices architecture pattern with the following key components:

```
┌─────────────────────────────────────────────────────────────┐
│                         Clients                              │
│                  (Web, Mobile, Desktop)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│                    (Port 8000)                               │
│  - Request Routing                                           │
│  - Load Balancing                                            │
│  - Health Monitoring                                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ User Service │  │Product Service│  │Order Service │
│  (Port 8001) │  │  (Port 8002)  │  │ (Port 8003)  │
└──────┬───────┘  └──────┬────────┘  └──────┬───────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   users.db   │  │ products.db  │  │  orders.db   │
└──────────────┘  └──────────────┘  └──────────────┘

        ┌──────────────────┬──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Payment Service│  │Report Service│  │Shared Models │
│  (Port 8004) │  │  (Port 8005) │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Design Patterns Used

### 1. Microservices Pattern
- **Purpose**: Decompose application into loosely coupled services
- **Benefits**: Independent deployment, scaling, and development

### 2. API Gateway Pattern
- **Purpose**: Single entry point for all client requests
- **Benefits**: Simplified client code, centralized cross-cutting concerns

### 3. Database per Service Pattern
- **Purpose**: Each service owns its data
- **Benefits**: Service independence, technology flexibility

### 4. Repository Pattern
- **Purpose**: Abstract data access logic
- **Implementation**: SQLAlchemy ORM

### 5. Dependency Injection
- **Purpose**: Loose coupling between components
- **Implementation**: FastAPI's dependency system

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications

### Database
- **SQLite**: Lightweight database for development
- **SQLAlchemy**: ORM for database operations

### Security
- **Passlib**: Password hashing library
- **Bcrypt**: Secure password hashing algorithm

### Testing
- **Pytest**: Testing framework
- **TestClient**: FastAPI's test client

### API Documentation
- **OpenAPI/Swagger**: Automatic API documentation

## Service Details

### User Service
**Responsibilities:**
- User registration
- Authentication
- User profile management

**Endpoints:**
- POST /register
- POST /login
- GET /users/{user_id}
- GET /health

**Database Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME
);
```

### Product Service
**Responsibilities:**
- Product catalog management
- Inventory tracking
- Stock management

**Endpoints:**
- POST /products
- GET /products
- GET /products/{product_id}
- PUT /products/{product_id}
- PATCH /products/{product_id}/stock
- GET /health

**Database Schema:**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at DATETIME
);
```

### Order Service
**Responsibilities:**
- Order creation
- Order management
- Coordination with other services

**Endpoints:**
- POST /orders
- GET /orders/{order_id}
- GET /orders/user/{user_id}
- GET /health

**Database Schema:**
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME
);
```

### Payment Service
**Responsibilities:**
- Payment processing
- Transaction management

**Endpoints:**
- POST /payments
- GET /health

### Reporting Service
**Responsibilities:**
- Sales analytics
- Inventory reports

**Endpoints:**
- GET /reports/sales
- GET /reports/inventory
- GET /health

## Communication Patterns

### Synchronous HTTP/REST
- Used for real-time operations
- Request-response pattern
- Direct service-to-service calls

### Error Handling
- Standard HTTP status codes
- Consistent error response format
- Service unavailability handling

## Scalability Considerations

### Horizontal Scaling
- Stateless services enable easy replication
- Load balancer can distribute requests
- Each service scales independently

### Database Scaling
- Read replicas for read-heavy services
- Sharding for large datasets
- Caching layer (future enhancement)

### Performance Optimization
- Connection pooling
- Async operations where applicable
- Efficient database queries

## Security Measures

### Authentication & Authorization
- Bcrypt password hashing
- Token-based auth (future enhancement)

### Data Validation
- Pydantic models for input validation
- Type checking
- SQL injection prevention via ORM

### Network Security
- CORS configuration
- HTTPS (production)
- Rate limiting (future enhancement)

## Monitoring & Observability

### Health Checks
- Each service exposes /health endpoint
- Gateway monitors all services
- Automated health status reporting

### Logging
- Structured logging
- Request/response logging
- Error tracking

### Metrics (Future)
- Request latency
- Error rates
- Service availability

## Deployment Strategy

### Development
- Local development with SQLite
- Each service runs independently
- Manual service startup

### Production (Recommended)
- Docker containers
- Kubernetes orchestration
- PostgreSQL/MySQL databases
- Redis caching
- Message queue (RabbitMQ/Kafka)

## Best Practices Implemented

1. **Single Responsibility**: Each service has one clear purpose
2. **DRY Principle**: Shared models in common module
3. **API Versioning**: Version in service title
4. **Documentation**: Auto-generated API docs
5. **Testing**: Unit tests for each service
6. **Error Handling**: Consistent error responses
7. **Code Organization**: Clear directory structure
8. **Type Hints**: Python type annotations
9. **Dependency Management**: Requirements files per service
10. **Health Monitoring**: Health check endpoints

## Migration Path from Legacy

1. **Analysis**: Identify modules and dependencies
2. **Database Separation**: Extract data models
3. **Service Extraction**: Create independent services
4. **API Layer**: Add REST endpoints
5. **Gateway Setup**: Configure routing
6. **Testing**: Validate functionality
7. **Documentation**: Generate docs
8. **Deployment**: Deploy services

## Conclusion

This architecture provides:
- ✅ Scalability
- ✅ Maintainability
- ✅ Reliability
- ✅ Flexibility
- ✅ Team autonomy
- ✅ Independent deployment
"""
        
        with open(f"{self.output_dir}/docs/architecture.md", 'w') as f:
            f.write(content)
    
    def _generate_api_documentation(self) -> None:
        """Generate API documentation"""
        
        content = """# API Documentation

## Base URL

All API requests should be made through the API Gateway:

```
http://localhost:8000
```

## Service Endpoints

### User Service

#### Register User
```http
POST /user/register
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "email": "string"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

#### Login User
```http
POST /user/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user_id": 1,
  "username": "john_doe"
}
```

#### Get User
```http
GET /user/users/{user_id}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

---

### Product Service

#### Create Product
```http
POST /product/products
Content-Type: application/json

{
  "name": "string",
  "price": 0.0,
  "stock": 0
}
```

#### Get All Products
```http
GET /product/products
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Laptop",
    "price": 999.99,
    "stock": 10
  }
]
```

#### Get Product
```http
GET /product/products/{product_id}
```

#### Update Product
```http
PUT /product/products/{product_id}
Content-Type: application/json

{
  "name": "string",
  "price": 0.0,
  "stock": 0
}
```

#### Update Stock
```http
PATCH /product/products/{product_id}/stock?quantity=5
```

---

### Order Service

#### Create Order
```http
POST /order/orders
Content-Type: application/json

{
  "user_id": 1,
  "product_id": 1,
  "quantity": 2
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "quantity": 2,
  "total": 1999.98,
  "status": "pending"
}
```

#### Get Order
```http
GET /order/orders/{order_id}
```

#### Get User Orders
```http
GET /order/orders/user/{user_id}
```

---

### Payment Service

#### Process Payment
```http
POST /payment/payments
Content-Type: application/json

{
  "order_id": 1,
  "payment_method": "credit_card",
  "amount": 1999.98
}
```

**Response:**
```json
{
  "transaction_id": "TXN-1-credit_card",
  "status": "success",
  "message": "Payment processed successfully via credit_card"
}
```

**Payment Methods:**
- `credit_card`
- `debit_card`
- `paypal`
- `bank_transfer`

---

### Reporting Service

#### Get Sales Report
```http
GET /reporting/reports/sales
```

**Response:**
```json
{
  "total_orders": 100,
  "total_revenue": 50000.00,
  "average_order_value": 500.00
}
```

#### Get Inventory Report
```http
GET /reporting/reports/inventory
```

**Response:**
```json
{
  "total_products": 50,
  "total_stock": 500,
  "low_stock_count": 5,
  "low_stock_items": [...]
}
```

---

## Health Checks

Each service provides a health check endpoint:

```http
GET /user/health
GET /product/health
GET /order/health
GET /payment/health
GET /reporting/health
```

Gateway health check (checks all services):
```http
GET /health
```

---

## Error Responses

All services return consistent error responses:

```json
{
  "detail": "Error message"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found
- `503 Service Unavailable`: Service is down

---

## Interactive Documentation

Each service provides interactive Swagger UI documentation:

- User Service: http://localhost:8001/docs
- Product Service: http://localhost:8002/docs
- Order Service: http://localhost:8003/docs
- Payment Service: http://localhost:8004/docs
- Reporting Service: http://localhost:8005/docs
- API Gateway: http://localhost:8000/docs

---

## Example Workflows

### Complete Purchase Flow

1. **Register User**
```bash
curl -X POST http://localhost:8000/user/register \\
  -H "Content-Type: application/json" \\
  -d '{"username":"john","password":"pass123","email":"john@example.com"}'
```

2. **Create Product**
```bash
curl -X POST http://localhost:8000/product/products \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Laptop","price":999.99,"stock":10}'
```

3. **Create Order**
```bash
curl -X POST http://localhost:8000/order/orders \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":1,"product_id":1,"quantity":1}'
```

4. **Process Payment**
```bash
curl -X POST http://localhost:8000/payment/payments \\
  -H "Content-Type: application/json" \\
  -d '{"order_id":1,"payment_method":"credit_card","amount":999.99}'
```

5. **View Reports**
```bash
curl http://localhost:8000/reporting/reports/sales
```
"""
        
        with open(f"{self.output_dir}/docs/api_documentation.md", 'w') as f:
            f.write(content)

# Made with Bob
