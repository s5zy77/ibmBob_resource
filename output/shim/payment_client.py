"""HTTP client for calling the Payment Service"""
import requests
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class PaymentServiceClient:
    """
    HTTP client for the Payment Service
    Handles communication between monolith and payment microservice
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 5):
        """
        Initialize payment service client
        
        Args:
            base_url: Base URL of payment service (e.g., http://localhost:8001)
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logger
    
    def process_payment(
        self,
        amount: float,
        method: str,
        currency: str = "USD",
        card: Optional[Dict[str, str]] = None,
        paypal_email: Optional[str] = None,
        order_id: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call the payment service to process a payment
        
        Args:
            amount: Payment amount
            method: Payment method (card, paypal, wire)
            currency: Currency code (default: USD)
            card: Card details dict with number, cvv, expiry (for card payments)
            paypal_email: PayPal email (for PayPal payments)
            order_id: Associated order ID
            customer_id: Customer ID
        
        Returns:
            Payment result dictionary with status, transaction_id, amount
            
        Raises:
            PaymentServiceTimeout: If request times out
            PaymentServiceError: If service returns error or is unavailable
        """
        url = f"{self.base_url}/api/v1/payments/process"
        
        # Build payload
        payload = {
            "amount": amount,
            "currency": currency,
            "method": method
        }
        
        # Add method-specific fields
        if method == "card" and card:
            payload["card"] = card
        elif method == "paypal" and paypal_email:
            payload["paypal_email"] = paypal_email
        
        # Add metadata
        if order_id:
            payload["order_id"] = order_id
        if customer_id:
            payload["customer_id"] = customer_id
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            self.logger.info(
                f"Calling payment service: method={method}, amount={amount}"
            )
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # Check for HTTP errors
            if response.status_code == 400:
                error_detail = response.json().get("detail", "Validation error")
                self.logger.error(f"Payment validation error: {error_detail}")
                raise PaymentServiceError(f"Validation error: {error_detail}")
            
            elif response.status_code == 401:
                self.logger.error("Payment service authentication failed")
                raise PaymentServiceError("Authentication failed")
            
            elif response.status_code == 403:
                self.logger.error("Payment service authorization failed")
                raise PaymentServiceError("Authorization failed")
            
            elif response.status_code >= 500:
                self.logger.error(f"Payment service error: {response.status_code}")
                raise PaymentServiceError("Payment service unavailable")
            
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(
                f"Payment successful: txn={result.get('transaction_id')}"
            )
            
            return result
        
        except requests.exceptions.Timeout:
            self.logger.error(f"Payment service timeout after {self.timeout}s")
            raise PaymentServiceTimeout(
                f"Payment service did not respond within {self.timeout}s"
            )
        
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Cannot connect to payment service: {e}")
            raise PaymentServiceError(
                "Cannot connect to payment service"
            )
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Payment service request error: {e}")
            raise PaymentServiceError(str(e))
    
    def health_check(self) -> bool:
        """
        Check if payment service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Payment service health check failed: {e}")
            return False
    
    def validate_payment(
        self,
        amount: float,
        method: str,
        currency: str = "USD",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate payment details without processing
        
        Args:
            amount: Payment amount
            method: Payment method
            currency: Currency code
            **kwargs: Method-specific parameters
            
        Returns:
            Validation result dictionary
        """
        url = f"{self.base_url}/api/v1/payments/validate"
        
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
        
        except Exception as e:
            self.logger.error(f"Payment validation error: {e}")
            return {"valid": False, "errors": [str(e)]}


class PaymentServiceTimeout(Exception):
    """Raised when payment service request times out"""
    pass


class PaymentServiceError(Exception):
    """Raised when payment service returns an error"""
    pass

# Made with Bob
