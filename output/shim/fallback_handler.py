"""Fallback handler with legacy payment logic"""
import time
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LegacyPaymentFallback:
    """
    Fallback to original payment logic when service is unavailable
    
    This is an exact copy of the payment processing logic from
    enterprise_monolith.py lines 262-303, preserved for fallback purposes
    """
    
    def __init__(
        self,
        payment_gateway_url: str,
        payment_api_key: str,
        max_retries: int = 3,
        currency: str = "USD"
    ):
        """
        Initialize legacy payment fallback
        
        Args:
            payment_gateway_url: Payment gateway URL
            payment_api_key: Payment API key
            max_retries: Maximum retry attempts
            currency: Default currency
        """
        self.payment_gateway_url = payment_gateway_url
        self.payment_api_key = payment_api_key
        self.max_retries = max_retries
        self.currency = currency
        
        logger.info("Legacy payment fallback initialized")
    
    def process_payment(
        self,
        amount: float,
        method: str,
        currency: str = "USD",
        card: Optional[Dict[str, str]] = None,
        paypal_email: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy payment processing logic
        
        Exact copy of original monolith code for fallback purposes
        
        Args:
            amount: Payment amount
            method: Payment method (card, paypal, wire)
            currency: Currency code
            card: Card details (for card payments)
            paypal_email: PayPal email (for PayPal payments)
            **kwargs: Additional parameters
            
        Returns:
            Payment result dictionary
        """
        logger.warning(
            f"[FALLBACK] Using legacy payment logic: method={method}, "
            f"amount={amount}"
        )
        
        try:
            if method == "card":
                return self._process_card_legacy(amount, currency, card or {})
            elif method == "paypal":
                return self._process_paypal_legacy(amount, paypal_email)
            elif method == "wire":
                return self._process_wire_legacy(amount)
            else:
                return {"status": "err", "msg": "unknown pay method"}
        
        except Exception as e:
            logger.error(f"[FALLBACK] Legacy payment failed: {e}")
            return {"status": "err", "msg": str(e)}
    
    def _process_card_legacy(
        self,
        amount: float,
        currency: str,
        card: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Legacy card payment processing
        Original code from lines 266-281
        """
        cn = str(card.get("number", ""))
        cv = str(card.get("cvv", ""))
        em = str(card.get("expiry", ""))
        
        # Validation (original logic)
        if len(cn) not in [15, 16]:
            return {"status": "err", "msg": "bad card number"}
        if len(cv) not in [3, 4]:
            return {"status": "err", "msg": "bad cvv"}
        if not re.match(r"^\d{2}/\d{2}$", em):
            return {"status": "err", "msg": "bad expiry"}
        
        # Retry logic (original)
        retries = 0
        while retries < self.max_retries:
            try:
                logger.info(
                    f"[PAY-LEGACY] POST {self.payment_gateway_url} "
                    f"key={self.payment_api_key[:10]}... "
                    f"amount={amount:.2f} cur={currency}"
                )
                time.sleep(0.02)
                
                # Success
                txn_id = "TXN" + str(int(time.time()))
                return {
                    "status": "ok",
                    "txn": txn_id,
                    "transaction_id": txn_id,  # Also include new format
                    "amount": amount
                }
            
            except Exception as ex:
                retries += 1
                if retries >= self.max_retries:
                    return {"status": "err", "msg": "payment gateway down"}
        
        return {"status": "err", "msg": "payment gateway down"}
    
    def _process_paypal_legacy(
        self,
        amount: float,
        paypal_email: Optional[str]
    ) -> Dict[str, Any]:
        """
        Legacy PayPal payment processing
        Original code from lines 282-288
        """
        if not paypal_email:
            return {"status": "err", "msg": "no paypal email"}
        
        if "@" not in paypal_email:
            return {"status": "err", "msg": "bad paypal email"}
        
        logger.info(
            f"[PAY-PP-LEGACY] paypal charge to {paypal_email} "
            f"amount={amount:.2f}"
        )
        time.sleep(0.02)
        
        txn_id = "PP" + str(int(time.time()))
        return {
            "status": "ok",
            "txn": txn_id,
            "transaction_id": txn_id,  # Also include new format
            "amount": amount
        }
    
    def _process_wire_legacy(self, amount: float) -> Dict[str, Any]:
        """
        Legacy wire transfer processing
        Original code from lines 289-294
        """
        if amount < 1000:
            return {"status": "err", "msg": "wire transfer minimum is 1000"}
        
        logger.info(f"[PAY-WIRE-LEGACY] wire transfer amount={amount:.2f}")
        time.sleep(0.02)
        
        txn_id = "WT" + str(int(time.time()))
        return {
            "status": "ok",
            "txn": txn_id,
            "transaction_id": txn_id,  # Also include new format
            "amount": amount
        }

# Made with Bob
