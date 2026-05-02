"""FastAPI routes for payment processing endpoints"""
import logging
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional

from payment_service.api.schemas import (
    PaymentRequest,
    PaymentResponse,
    HealthResponse
)
from payment_service.domain.payment_processor import PaymentProcessor
from payment_service.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key from request header
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        Verified API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if x_api_key not in settings.API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return x_api_key


def get_payment_processor() -> PaymentProcessor:
    """Dependency injection for PaymentProcessor"""
    return PaymentProcessor()


@router.post("/payments/process", response_model=PaymentResponse)
async def process_payment(
    request: PaymentRequest,
    processor: PaymentProcessor = Depends(get_payment_processor),
    api_key: str = Depends(verify_api_key)
) -> PaymentResponse:
    """
    Process a payment transaction
    
    Supports three payment methods:
    - **card**: Credit/debit card payment (requires card details)
    - **paypal**: PayPal payment (requires PayPal email)
    - **wire**: Wire transfer (minimum $1000)
    
    Args:
        request: Payment request with amount, method, and payment details
        processor: Payment processor instance (injected)
        api_key: Verified API key (injected)
        
    Returns:
        PaymentResponse with transaction ID and status
        
    Raises:
        HTTPException: For validation or processing errors
    """
    try:
        logger.info(
            f"Payment request: method={request.method}, "
            f"amount={request.amount}, "
            f"order_id={request.order_id}"
        )
        
        result = await processor.process(request)
        
        if result.status == "err":
            logger.error(f"Payment failed: {result.message}")
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"Payment successful: txn={result.transaction_id}")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        raise HTTPException(status_code=500, detail="Payment processing failed")


@router.post("/payments/validate")
async def validate_payment(
    request: PaymentRequest,
    processor: PaymentProcessor = Depends(get_payment_processor),
    api_key: str = Depends(verify_api_key)
) -> dict:
    """
    Validate payment details without processing
    
    Useful for pre-validation before actual payment processing
    
    Args:
        request: Payment request to validate
        processor: Payment processor instance (injected)
        api_key: Verified API key (injected)
        
    Returns:
        Validation result with any errors
    """
    try:
        validation_result = processor.validate_payment(request)
        return validation_result
    
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payments/{transaction_id}")
async def get_payment_status(
    transaction_id: str,
    api_key: str = Depends(verify_api_key)
) -> dict:
    """
    Retrieve payment transaction status
    
    Note: This is a placeholder for future implementation
    In production, this would query a payment transaction database
    
    Args:
        transaction_id: Transaction ID to look up
        api_key: Verified API key (injected)
        
    Returns:
        Transaction status information
    """
    # Placeholder implementation
    # In production, query database for transaction
    return {
        "transaction_id": transaction_id,
        "status": "completed",
        "message": "Transaction lookup not yet implemented"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    
    Returns service health status without requiring authentication
    Used by load balancers and monitoring systems
    
    Returns:
        HealthResponse with service status
    """
    from payment_service import __version__
    
    return HealthResponse(
        status="healthy",
        service="payment-service",
        version=__version__
    )

# Made with Bob
