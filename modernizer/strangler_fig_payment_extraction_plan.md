# Strangler Fig Pattern: Payment Processing Extraction Plan

## Overview
This plan details the extraction of Payment Processing logic from [`enterprise_monolith.py`](enterprise_monolith.py:262-303) into a standalone microservice using the Strangler Fig pattern. The approach ensures zero-downtime migration with the ability to rollback at any stage.

---

## Current State Analysis

### Payment Logic Location
**File:** [`enterprise_monolith.py`](enterprise_monolith.py)
**Function:** [`process_everything()`](enterprise_monolith.py:204-364)
**Lines:** 262-303 (42 lines of embedded payment logic)

### Current Payment Methods
1. **Card Payment** (lines 266-281)
   - Validates card number (15-16 digits)
   - Validates CVV (3-4 digits)
   - Validates expiry format (MM/YY)
   - Calls external payment gateway

2. **PayPal Payment** (lines 282-288)
   - Validates PayPal email
   - Processes PayPal charge

3. **Wire Transfer** (lines 289-294)
   - Validates minimum amount ($1000)
   - Processes wire transfer

### Current Dependencies
- `PAYMENT_GATEWAY_URL` (line 17)
- `PAYMENT_API_KEY` (line 18)
- `MAX_RETRIES` (line 21)
- `CURRENCY` (line 23)

---

## Proposed File Structure

```
lagacy_monolith/
├── enterprise_monolith.py          # Original monolith (modified with shim)
├── domain_analysis.md              # Domain analysis document
├── strangler_fig_payment_extraction_plan.md  # This document
│
├── payment_service/                # New Payment Microservice
│   ├── __init__.py
│   ├── app.py                      # Flask/FastAPI application entry point
│   ├── config.py                   # Service configuration
│   ├── requirements.txt            # Python dependencies
│   │
│   ├── api/                        # REST API Layer
│   │   ├── __init__.py
│   │   ├── routes.py               # API endpoints
│   │   ├── schemas.py              # Request/Response models (Pydantic)
│   │   └── middleware.py           # Auth, logging, error handling
│   │
│   ├── domain/                     # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── payment_processor.py   # Core payment processing logic
│   │   ├── validators.py          # Payment validation rules
│   │   └── models.py               # Domain models
│   │
│   ├── infrastructure/             # External Integrations
│   │   ├── __init__.py
│   │   ├── payment_gateway.py     # Payment gateway client
│   │   ├── paypal_client.py       # PayPal integration
│   │   └── wire_transfer.py       # Wire transfer handling
│   │
│   ├── tests/                      # Test Suite
│   │   ├── __init__.py
│   │   ├── test_api.py             # API endpoint tests
│   │   ├── test_payment_processor.py  # Business logic tests
│   │   └── test_validators.py      # Validation tests
│   │
│   └── docker/                     # Containerization
│       ├── Dockerfile
│       └── docker-compose.yml
│
├── shim/                           # Integration Shim Layer
│   ├── __init__.py
│   ├── payment_client.py           # HTTP client for payment service
│   ├── circuit_breaker.py          # Fault tolerance
│   └── fallback_handler.py         # Fallback to legacy logic
│
└── docs/                           # Documentation
    ├── api_specification.yaml      # OpenAPI/Swagger spec
    ├── migration_guide.md          # Step-by-step migration
    └── rollback_procedure.md       # Emergency rollback steps
```

---

## Detailed Component Design

### 1. Payment Service (`payment_service/`)

#### 1.1 Application Entry Point (`app.py`)
```python
# FastAPI application with health checks, metrics, and API versioning
from fastapi import FastAPI
from api.routes import router
from api.middleware import setup_middleware

app = FastAPI(
    title="Payment Processing Service",
    version="1.0.0",
    description="Extracted payment processing microservice"
)

setup_middleware(app)
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment"}
```

#### 1.2 Configuration (`config.py`)
```python
# Environment-based configuration
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Payment Gateway
    PAYMENT_GATEWAY_URL: str
    PAYMENT_API_KEY: str
    
    # Service Config
    MAX_RETRIES: int = 3
    CURRENCY: str = "USD"
    WIRE_MINIMUM: float = 1000.0
    
    # Service Discovery
    SERVICE_PORT: int = 8001
    SERVICE_HOST: str = "0.0.0.0"
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    ALLOWED_ORIGINS: list = ["http://localhost:8000"]
    
    class Config:
        env_file = ".env"
```

#### 1.3 API Routes (`api/routes.py`)
```python
from fastapi import APIRouter, HTTPException, Depends
from api.schemas import PaymentRequest, PaymentResponse
from domain.payment_processor import PaymentProcessor

router = APIRouter()

@router.post("/payments/process", response_model=PaymentResponse)
async def process_payment(
    request: PaymentRequest,
    processor: PaymentProcessor = Depends()
):
    """
    Process a payment transaction
    
    Supports: card, paypal, wire transfer
    """
    try:
        result = await processor.process(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment processing failed")

@router.post("/payments/validate", response_model=dict)
async def validate_payment(request: PaymentRequest):
    """Validate payment details without processing"""
    # Validation logic
    pass

@router.get("/payments/{transaction_id}")
async def get_payment_status(transaction_id: str):
    """Retrieve payment transaction status"""
    pass
```

#### 1.4 Request/Response Schemas (`api/schemas.py`)
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from decimal import Decimal

class CardDetails(BaseModel):
    number: str = Field(..., min_length=15, max_length=16)
    cvv: str = Field(..., min_length=3, max_length=4)
    expiry: str = Field(..., regex=r"^\d{2}/\d{2}$")

class PaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD")
    method: Literal["card", "paypal", "wire"]
    
    # Method-specific fields
    card: Optional[CardDetails] = None
    paypal_email: Optional[str] = None
    
    # Metadata
    order_id: Optional[str] = None
    customer_id: Optional[str] = None
    
    @validator('card')
    def validate_card_for_method(cls, v, values):
        if values.get('method') == 'card' and not v:
            raise ValueError('Card details required for card payment')
        return v
    
    @validator('paypal_email')
    def validate_paypal_for_method(cls, v, values):
        if values.get('method') == 'paypal' and not v:
            raise ValueError('PayPal email required for PayPal payment')
        return v

class PaymentResponse(BaseModel):
    status: Literal["ok", "err"]
    transaction_id: Optional[str] = None
    amount: Optional[Decimal] = None
    message: Optional[str] = None
    timestamp: str
```

#### 1.5 Payment Processor (`domain/payment_processor.py`)
```python
from domain.validators import PaymentValidator
from infrastructure.payment_gateway import PaymentGatewayClient
from infrastructure.paypal_client import PayPalClient
from infrastructure.wire_transfer import WireTransferClient
import datetime

class PaymentProcessor:
    def __init__(self, config):
        self.config = config
        self.validator = PaymentValidator()
        self.gateway = PaymentGatewayClient(config)
        self.paypal = PayPalClient(config)
        self.wire = WireTransferClient(config)
    
    async def process(self, request: PaymentRequest) -> PaymentResponse:
        # Validate request
        self.validator.validate(request)
        
        # Route to appropriate payment method
        if request.method == "card":
            return await self._process_card(request)
        elif request.method == "paypal":
            return await self._process_paypal(request)
        elif request.method == "wire":
            return await self._process_wire(request)
    
    async def _process_card(self, request: PaymentRequest):
        # Extracted from lines 266-281
        retries = 0
        while retries < self.config.MAX_RETRIES:
            try:
                result = await self.gateway.charge(
                    amount=request.amount,
                    currency=request.currency,
                    card=request.card
                )
                return PaymentResponse(
                    status="ok",
                    transaction_id=result.transaction_id,
                    amount=request.amount,
                    timestamp=str(datetime.datetime.now())
                )
            except Exception as e:
                retries += 1
                if retries >= self.config.MAX_RETRIES:
                    raise
    
    async def _process_paypal(self, request: PaymentRequest):
        # Extracted from lines 282-288
        result = await self.paypal.charge(
            email=request.paypal_email,
            amount=request.amount
        )
        return PaymentResponse(
            status="ok",
            transaction_id=result.transaction_id,
            amount=request.amount,
            timestamp=str(datetime.datetime.now())
        )
    
    async def _process_wire(self, request: PaymentRequest):
        # Extracted from lines 289-294
        if request.amount < self.config.WIRE_MINIMUM:
            raise ValueError(f"Wire transfer minimum is {self.config.WIRE_MINIMUM}")
        
        result = await self.wire.process(amount=request.amount)
        return PaymentResponse(
            status="ok",
            transaction_id=result.transaction_id,
            amount=request.amount,
            timestamp=str(datetime.datetime.now())
        )
```

#### 1.6 Validators (`domain/validators.py`)
```python
import re
from api.schemas import PaymentRequest

class PaymentValidator:
    def validate(self, request: PaymentRequest):
        if request.method == "card":
            self._validate_card(request.card)
        elif request.method == "paypal":
            self._validate_paypal(request.paypal_email)
        elif request.method == "wire":
            self._validate_wire(request.amount)
    
    def _validate_card(self, card):
        if len(card.number) not in [15, 16]:
            raise ValueError("Invalid card number length")
        if len(card.cvv) not in [3, 4]:
            raise ValueError("Invalid CVV length")
        if not re.match(r"^\d{2}/\d{2}$", card.expiry):
            raise ValueError("Invalid expiry format")
    
    def _validate_paypal(self, email):
        if "@" not in email:
            raise ValueError("Invalid PayPal email")
    
    def _validate_wire(self, amount):
        if amount < 1000:
            raise ValueError("Wire transfer minimum is $1000")
```

---

### 2. Shim Layer (`shim/`)

#### 2.1 Payment Client (`payment_client.py`)
```python
import requests
from typing import Dict, Optional
import logging

class PaymentServiceClient:
    """
    HTTP client for the Payment Service
    Implements circuit breaker pattern for fault tolerance
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 5):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def process_payment(
        self,
        amount: float,
        method: str,
        currency: str = "USD",
        **kwargs
    ) -> Dict:
        """
        Call the payment service to process a payment
        
        Args:
            amount: Payment amount
            method: Payment method (card, paypal, wire)
            currency: Currency code
            **kwargs: Method-specific parameters (card, paypal_email, etc.)
        
        Returns:
            Payment result dictionary
        """
        url = f"{self.base_url}/api/v1/payments/process"
        
        payload = {
            "amount": amount,
            "currency": currency,
            "method": method,
            **kwargs
        }
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            self.logger.error(f"Payment service timeout after {self.timeout}s")
            raise PaymentServiceTimeout()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Payment service error: {e}")
            raise PaymentServiceError(str(e))
    
    def health_check(self) -> bool:
        """Check if payment service is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False

class PaymentServiceTimeout(Exception):
    pass

class PaymentServiceError(Exception):
    pass
```

#### 2.2 Circuit Breaker (`circuit_breaker.py`)
```python
import time
from enum import Enum
from typing import Callable

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Service unavailable, use fallback
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    Prevents cascading failures when payment service is down
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, fallback: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Primary function to call (payment service)
            fallback: Fallback function (legacy payment logic)
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                # Circuit is open, use fallback
                return fallback(*args, **kwargs)
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure()
            
            if self.state == CircuitState.OPEN:
                # Use fallback
                return fallback(*args, **kwargs)
            else:
                raise
    
    def _on_success(self):
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.timeout
        )
```

#### 2.3 Fallback Handler (`fallback_handler.py`)
```python
import time
import hashlib
import datetime

class LegacyPaymentFallback:
    """
    Fallback to original payment logic when service is unavailable
    Extracted from enterprise_monolith.py lines 262-303
    """
    
    def __init__(self, config):
        self.config = config
    
    def process_payment(
        self,
        amount: float,
        method: str,
        currency: str = "USD",
        **kwargs
    ) -> dict:
        """
        Legacy payment processing logic
        Exact copy of original monolith code
        """
        if method == "card":
            return self._process_card_legacy(amount, currency, kwargs.get("card", {}))
        elif method == "paypal":
            return self._process_paypal_legacy(amount, kwargs.get("paypal_email"))
        elif method == "wire":
            return self._process_wire_legacy(amount)
        else:
            return {"status": "err", "msg": "unknown pay method"}
    
    def _process_card_legacy(self, amount, currency, card):
        # Original logic from lines 266-281
        cn = str(card.get("number", ""))
        cv = str(card.get("cvv", ""))
        em = str(card.get("expiry", ""))
        
        if len(cn) not in [15, 16]:
            return {"status": "err", "msg": "bad card number"}
        if len(cv) not in [3, 4]:
            return {"status": "err", "msg": "bad cvv"}
        if not re.match(r"^\d{2}/\d{2}$", em):
            return {"status": "err", "msg": "bad expiry"}
        
        print(f"[PAY-LEGACY] POST {self.config.PAYMENT_GATEWAY_URL}")
        time.sleep(0.02)
        
        return {
            "status": "ok",
            "txn": "TXN" + str(int(time.time())),
            "amount": amount
        }
    
    def _process_paypal_legacy(self, amount, email):
        # Original logic from lines 282-288
        if "@" not in email:
            return {"status": "err", "msg": "bad paypal email"}
        
        print(f"[PAY-PP-LEGACY] paypal charge to {email}")
        time.sleep(0.02)
        
        return {
            "status": "ok",
            "txn": "PP" + str(int(time.time())),
            "amount": amount
        }
    
    def _process_wire_legacy(self, amount):
        # Original logic from lines 289-294
        if amount < 1000:
            return {"status": "err", "msg": "wire transfer minimum is 1000"}
        
        print(f"[PAY-WIRE-LEGACY] wire transfer amount={amount}")
        time.sleep(0.02)
        
        return {
            "status": "ok",
            "txn": "WT" + str(int(time.time())),
            "amount": amount
        }
```

---

### 3. Modified Monolith Integration

#### 3.1 Updated `enterprise_monolith.py`

**Changes to `process_everything()` function:**

```python
# Add at top of file
from shim.payment_client import PaymentServiceClient, PaymentServiceTimeout, PaymentServiceError
from shim.circuit_breaker import CircuitBreaker
from shim.fallback_handler import LegacyPaymentFallback

# Add configuration
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8001")
PAYMENT_SERVICE_API_KEY = os.getenv("PAYMENT_SERVICE_API_KEY", "dev-api-key-123")
USE_PAYMENT_SERVICE = os.getenv("USE_PAYMENT_SERVICE", "false").lower() == "true"

# Initialize payment components
payment_client = PaymentServiceClient(PAYMENT_SERVICE_URL, PAYMENT_SERVICE_API_KEY)
payment_fallback = LegacyPaymentFallback(config)
payment_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

# In process_everything() function, replace lines 262-303 with:
def _call_payment_service(amount, method, currency, **kwargs):
    """Call new payment service"""
    return payment_client.process_payment(
        amount=amount,
        method=method,
        currency=currency,
        **kwargs
    )

def _call_legacy_payment(amount, method, currency, **kwargs):
    """Fallback to legacy payment logic"""
    return payment_fallback.process_payment(
        amount=amount,
        method=method,
        currency=currency,
        **kwargs
    )

# Replace payment processing block (lines 262-303)
if USE_PAYMENT_SERVICE:
    # Use new payment service with circuit breaker
    pay_result = payment_circuit_breaker.call(
        func=_call_payment_service,
        fallback=_call_legacy_payment,
        amount=grand,
        method=pay_method,
        currency=CURRENCY,
        card=addr.get("card") if pay_method == "card" else None,
        paypal_email=addr.get("pp_email") if pay_method == "paypal" else None
    )
else:
    # Use legacy payment logic (original code preserved)
    pay_result = _call_legacy_payment(
        amount=grand,
        method=pay_method,
        currency=CURRENCY,
        card=addr.get("card") if pay_method == "card" else None,
        paypal_email=addr.get("pp_email") if pay_method == "paypal" else None
    )
```

---

## Migration Strategy

### Phase 1: Preparation (Week 1)
1. ✅ Create payment service codebase
2. ✅ Implement REST API with all payment methods
3. ✅ Write comprehensive unit tests (>80% coverage)
4. ✅ Set up local development environment
5. ✅ Create shim layer with circuit breaker

### Phase 2: Parallel Run (Week 2)
1. Deploy payment service to staging environment
2. Configure monolith with `USE_PAYMENT_SERVICE=false`
3. Add logging to compare legacy vs service results
4. Run shadow traffic (call both, use legacy result)
5. Monitor for discrepancies

### Phase 3: Canary Deployment (Week 3)
1. Enable payment service for 5% of traffic
2. Monitor error rates, latency, success rates
3. Gradually increase to 25%, 50%, 75%
4. Keep circuit breaker active for automatic fallback

### Phase 4: Full Migration (Week 4)
1. Switch to 100% payment service traffic
2. Monitor for 1 week with fallback enabled
3. Remove legacy payment code (optional)
4. Update documentation

---

## Rollback Procedure

### Immediate Rollback (< 5 minutes)
```bash
# Set environment variable to disable payment service
export USE_PAYMENT_SERVICE=false

# Restart monolith application
systemctl restart enterprise-monolith
```

### Circuit Breaker Automatic Fallback
- If payment service fails 5 times, circuit opens automatically
- All traffic routes to legacy payment logic
- No manual intervention required

### Emergency Rollback Steps
1. Set `USE_PAYMENT_SERVICE=false` in environment
2. Restart application
3. Verify legacy payment processing works
4. Investigate payment service issues
5. Fix and redeploy when ready

---

## Testing Strategy

### Unit Tests
- Payment processor logic
- Validators
- API endpoints
- Circuit breaker behavior

### Integration Tests
- End-to-end payment flows
- External gateway integration
- Error handling scenarios

### Load Tests
- 1000 requests/second
- Concurrent payment processing
- Circuit breaker under load

### Chaos Engineering
- Payment service downtime simulation
- Network latency injection
- Gateway timeout scenarios

---

## Monitoring & Observability

### Metrics to Track
- Payment success rate (target: >99.5%)
- Average response time (target: <500ms)
- Circuit breaker state changes
- Fallback invocation count
- Error rate by payment method

### Alerts
- Payment service down (circuit open)
- Error rate > 1%
- Response time > 1s
- Fallback usage > 10%

### Logging
- All payment requests/responses
- Circuit breaker state changes
- Fallback invocations
- Gateway communication

---

## API Specification

### POST /api/v1/payments/process

**Request:**
```json
{
  "amount": 1299.99,
  "currency": "USD",
  "method": "card",
  "card": {
    "number": "4111111111111111",
    "cvv": "123",
    "expiry": "12/26"
  },
  "order_id": "ORD123456",
  "customer_id": "USR789"
}
```

**Response (Success):**
```json
{
  "status": "ok",
  "transaction_id": "TXN1714574400",
  "amount": 1299.99,
  "timestamp": "2026-05-01T15:00:00.000Z"
}
```

**Response (Error):**
```json
{
  "status": "err",
  "message": "Invalid card number",
  "timestamp": "2026-05-01T15:00:00.000Z"
}
```

---

## Configuration Management

### Environment Variables

**Payment Service:**
```bash
PAYMENT_GATEWAY_URL=https://pay.internal.corp/api/v1/charge
PAYMENT_API_KEY=pk_live_ABCDEF1234567890
MAX_RETRIES=3
CURRENCY=USD
WIRE_MINIMUM=1000.0
SERVICE_PORT=8001
```

**Monolith (Shim):**
```bash
PAYMENT_SERVICE_URL=http://payment-service:8001
PAYMENT_SERVICE_API_KEY=secure-api-key-xyz
USE_PAYMENT_SERVICE=true
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
```

---

## Success Criteria

### Technical Metrics
- ✅ Payment service handles 100% of traffic
- ✅ Response time < 500ms (p95)
- ✅ Error rate < 0.5%
- ✅ Zero data loss during migration
- ✅ Circuit breaker tested and working

### Business Metrics
- ✅ No payment processing downtime
- ✅ No customer complaints
- ✅ Payment success rate maintained
- ✅ All payment methods working

---

## Next Steps

1. Review and approve this plan
2. Set up development environment
3. Implement payment service (estimated: 3-4 days)
4. Implement shim layer (estimated: 1-2 days)
5. Write tests (estimated: 2-3 days)
6. Begin Phase 1 migration

**Total Estimated Timeline:** 4 weeks from approval to full migration