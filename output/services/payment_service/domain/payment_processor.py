"""Core payment processing business logic - Extracted from enterprise_monolith.py"""
import time
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

from payment_service.api.schemas import PaymentRequest, PaymentResponse
from payment_service.config import settings

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """
    Core payment processing logic extracted from enterprise_monolith.py (lines 262-303)
    Handles card, PayPal, and wire transfer payments
    """
    
    def __init__(self):
        self.config = settings
        self.max_retries = settings.MAX_RETRIES
    
    async def process(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process a payment request
        
        Args:
            request: PaymentRequest with amount, method, and payment details
            
        Returns:
            PaymentResponse with transaction ID and status
            
        Raises:
            ValueError: For validation errors
            Exception: For payment processing failures
        """
        logger.info(f"Processing {request.method} payment for ${request.amount}")
        
        try:
            # Route to appropriate payment method
            if request.method == "card":
                return await self._process_card(request)
            elif request.method == "paypal":
                return await self._process_paypal(request)
            elif request.method == "wire":
                return await self._process_wire(request)
            else:
                raise ValueError(f"Unknown payment method: {request.method}")
        
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return PaymentResponse(
                status="err",
                message=str(e),
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            return PaymentResponse(
                status="err",
                message="Payment processing failed",
                timestamp=datetime.now().isoformat()
            )
    
    async def _process_card(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process card payment - Extracted from lines 266-281
        
        Implements retry logic for payment gateway calls
        """
        if not request.card:
            raise ValueError("Card details required for card payment")
        
        card = request.card
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                # Simulate payment gateway call
                logger.info(
                    f"[PAY] POST {self.config.PAYMENT_GATEWAY_URL} "
                    f"key={self.config.PAYMENT_API_KEY[:10]}... "
                    f"amount={float(request.amount):.2f} "
                    f"cur={request.currency}"
                )
                
                # Simulate network delay
                time.sleep(0.02)
                
                # Generate transaction ID
                txn_id = f"TXN{int(time.time())}"
                
                logger.info(f"Card payment successful: {txn_id}")
                
                return PaymentResponse(
                    status="ok",
                    transaction_id=txn_id,
                    amount=request.amount,
                    timestamp=datetime.now().isoformat()
                )
            
            except Exception as e:
                retries += 1
                last_error = e
                logger.warning(f"Card payment attempt {retries} failed: {e}")
                
                if retries >= self.max_retries:
                    logger.error(f"Card payment failed after {self.max_retries} retries")
                    raise Exception("Payment gateway down") from last_error
                
                # Wait before retry
                time.sleep(0.1 * retries)
        
        raise Exception("Payment gateway down")
    
    async def _process_paypal(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process PayPal payment - Extracted from lines 282-288
        """
        if not request.paypal_email:
            raise ValueError("PayPal email required for PayPal payment")
        
        if '@' not in request.paypal_email:
            raise ValueError("Invalid PayPal email format")
        
        logger.info(
            f"[PAY-PP] paypal charge to {request.paypal_email} "
            f"amount={float(request.amount):.2f}"
        )
        
        # Simulate PayPal API call
        time.sleep(0.02)
        
        # Generate transaction ID
        txn_id = f"PP{int(time.time())}"
        
        logger.info(f"PayPal payment successful: {txn_id}")
        
        return PaymentResponse(
            status="ok",
            transaction_id=txn_id,
            amount=request.amount,
            timestamp=datetime.now().isoformat()
        )
    
    async def _process_wire(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process wire transfer - Extracted from lines 289-294
        """
        if request.amount < Decimal(str(self.config.WIRE_MINIMUM)):
            raise ValueError(
                f"Wire transfer minimum is ${self.config.WIRE_MINIMUM}"
            )
        
        logger.info(
            f"[PAY-WIRE] wire transfer amount={float(request.amount):.2f}"
        )
        
        # Simulate wire transfer processing
        time.sleep(0.02)
        
        # Generate transaction ID
        txn_id = f"WT{int(time.time())}"
        
        logger.info(f"Wire transfer successful: {txn_id}")
        
        return PaymentResponse(
            status="ok",
            transaction_id=txn_id,
            amount=request.amount,
            timestamp=datetime.now().isoformat()
        )
    
    def validate_payment(self, request: PaymentRequest) -> Dict[str, Any]:
        """
        Validate payment details without processing
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        if request.method == "card":
            if not request.card:
                errors.append("Card details required")
            elif request.card:
                if len(request.card.number) not in [15, 16]:
                    errors.append("Invalid card number length")
                if len(request.card.cvv) not in [3, 4]:
                    errors.append("Invalid CVV length")
        
        elif request.method == "paypal":
            if not request.paypal_email:
                errors.append("PayPal email required")
            elif '@' not in request.paypal_email:
                errors.append("Invalid PayPal email")
        
        elif request.method == "wire":
            if request.amount < Decimal(str(self.config.WIRE_MINIMUM)):
                errors.append(f"Wire transfer minimum is ${self.config.WIRE_MINIMUM}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

# Made with Bob
