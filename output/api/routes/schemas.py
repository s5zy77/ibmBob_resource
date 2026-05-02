"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime


class CardDetails(BaseModel):
    """Credit/Debit card payment details"""
    number: str = Field(..., min_length=15, max_length=16, description="Card number (15-16 digits)")
    cvv: str = Field(..., min_length=3, max_length=4, description="CVV code (3-4 digits)")
    expiry: str = Field(..., pattern=r"^\d{2}/\d{2}$", description="Expiry date (MM/YY format)")
    
    @field_validator('number')
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Validate card number is numeric and correct length"""
        if not v.isdigit():
            raise ValueError('Card number must contain only digits')
        if len(v) not in [15, 16]:
            raise ValueError('Card number must be 15 or 16 digits')
        return v
    
    @field_validator('cvv')
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        """Validate CVV is numeric and correct length"""
        if not v.isdigit():
            raise ValueError('CVV must contain only digits')
        if len(v) not in [3, 4]:
            raise ValueError('CVV must be 3 or 4 digits')
        return v


class PaymentRequest(BaseModel):
    """Payment processing request"""
    amount: Decimal = Field(..., gt=0, description="Payment amount (must be positive)")
    currency: str = Field(default="USD", description="Currency code")
    method: Literal["card", "paypal", "wire"] = Field(..., description="Payment method")
    
    # Method-specific fields
    card: Optional[CardDetails] = Field(None, description="Card details (required for card payments)")
    paypal_email: Optional[str] = Field(None, description="PayPal email (required for PayPal payments)")
    
    # Metadata
    order_id: Optional[str] = Field(None, description="Associated order ID")
    customer_id: Optional[str] = Field(None, description="Customer ID")
    
    @field_validator('card')
    @classmethod
    def validate_card_for_method(cls, v: Optional[CardDetails], info) -> Optional[CardDetails]:
        """Ensure card details provided when method is 'card'"""
        if info.data.get('method') == 'card' and not v:
            raise ValueError('Card details required for card payment')
        return v
    
    @field_validator('paypal_email')
    @classmethod
    def validate_paypal_for_method(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure PayPal email provided when method is 'paypal'"""
        if info.data.get('method') == 'paypal':
            if not v:
                raise ValueError('PayPal email required for PayPal payment')
            if '@' not in v:
                raise ValueError('Invalid PayPal email format')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_wire_minimum(cls, v: Decimal, info) -> Decimal:
        """Validate wire transfer minimum amount"""
        if info.data.get('method') == 'wire' and v < 1000:
            raise ValueError('Wire transfer minimum is $1000')
        return v


class PaymentResponse(BaseModel):
    """Payment processing response"""
    status: Literal["ok", "err"] = Field(..., description="Payment status")
    transaction_id: Optional[str] = Field(None, description="Transaction ID (on success)")
    amount: Optional[Decimal] = Field(None, description="Processed amount")
    message: Optional[str] = Field(None, description="Error message (on failure)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Processing timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "transaction_id": "TXN1714574400",
                "amount": 1299.99,
                "timestamp": "2026-05-01T16:00:00.000Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Made with Bob
