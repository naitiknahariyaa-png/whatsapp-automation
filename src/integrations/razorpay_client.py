"""
Razorpay Integration - Indian Payment Gateway
Accept UPI, Cards, Wallets payments
"""

import os
import logging
import requests
import hashlib
import hmac
import json
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RazorpayClient:
    """
    Razorpay Payment Gateway Client
    
    Perfect for Indian businesses - supports:
    - UPI (Google Pay, PhonePe, Paytm)
    - Credit/Debit Cards
    - Net Banking
    - Wallets
    
    Setup:
    1. Sign up at https://razorpay.com
    2. Get API Key from Dashboard → Settings → API Keys
    3. Add to .env
    
    Environment:
    - RAZORPAY_KEY_ID=your_key_id
    - RAZORPAY_KEY_SECRET=your_key_secret
    """
    
    BASE_URL = "https://api.razorpay.com/v1"
    
    def __init__(
        self,
        key_id: Optional[str] = None,
        key_secret: Optional[str] = None
    ):
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID", "")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET", "")
        self.enabled = bool(self.key_id and self.key_secret)
        
        if self.enabled:
            logger.info("✅ Razorpay configured")
            self.auth = (self.key_id, self.key_secret)
        else:
            logger.warning("⚠️ Razorpay not configured (set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET)")
    
    def create_order(
        self,
        amount: int,
        currency: str = "INR",
        receipt: Optional[str] = None,
        notes: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create a new payment order
        
        Args:
            amount: Amount in paise (₹100 = 10000 paise)
            currency: Currency code (INR)
            receipt: Unique receipt ID
            notes: Additional notes
            
        Returns:
            Order dict with id, amount, currency, status
        """
        if not self.enabled:
            return None
        
        data = {
            "amount": amount,
            "currency": currency,
            "receipt": receipt or f"rcpt_{datetime.now().timestamp()}",
            "notes": notes or {}
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/orders",
                auth=self.auth,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Razorpay error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Razorpay request error: {e}")
            return None
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order details"""
        if not self.enabled:
            return None
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/orders/{order_id}",
                auth=self.auth,
                timeout=30
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Get order error: {e}")
            return None
    
    def create_payment_link(
        self,
        amount: int,
        description: str,
        customer_name: str,
        customer_email: str,
        customer_mobile: str,
        expiry_minutes: int = 30
    ) -> Optional[Dict]:
        """
        Create a payment link to send to customer
        
        Perfect for WhatsApp - just share the link!
        """
        if not self.enabled:
            return None
        
        from datetime import timedelta
        
        data = {
            "amount": amount,
            "currency": "INR",
            "accept_partial": False,
            "description": description,
            "customer": {
                "name": customer_name,
                "email": customer_email,
                "contact": customer_mobile
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "reminder_enable": True,
            "expire_by": int((datetime.now() + timedelta(minutes=expiry_minutes)).timestamp())
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/payment-links",
                auth=self.auth,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "id": result["id"],
                    "short_url": result["short_url"],
                    "amount": result["amount"],
                    "currency": result["currency"],
                    "status": result["status"]
                }
            return None
            
        except Exception as e:
            logger.error(f"Payment link error: {e}")
            return None
    
    def verify_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify payment signature
        
        IMPORTANT: Always verify before delivering product!
        """
        if not self.enabled:
            return False
        
        payload = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            self.key_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return razorpay_signature == expected_signature
    
    def refund(self, payment_id: str, amount: Optional[int] = None) -> Optional[Dict]:
        """
        Refund a payment
        
        Args:
            payment_id: Razorpay payment ID
            amount: Amount to refund in paise (None = full refund)
        """
        if not self.enabled:
            return None
        
        data = {}
        if amount:
            data["amount"] = amount
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/payments/{payment_id}/refund",
                auth=self.auth,
                json=data if data else None,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Refund error: {e}")
            return None


def setup_razorpay():
    """Interactive setup for Razorpay"""
    print("\n" + "="*50)
    print("💰 Razorpay Setup")
    print("="*50 + "\n")
    
    print("How to get Razorpay API keys:")
    print("1. Sign up at https://razorpay.com")
    print("2. Go to Dashboard → Settings → API Keys")
    print("3. Generate Key ID and Key Secret")
    print("4. Paste them below\n")
    
    key_id = input("Key ID (rzp_...): ").strip()
    key_secret = input("Key Secret: ").strip()
    
    if key_id and key_secret:
        with open(".env", "a") as f:
            f.write(f"\n# Razorpay Payment Gateway\n")
            f.write(f"RAZORPAY_KEY_ID={key_id}\n")
            f.write(f"RAZORPAY_KEY_SECRET={key_secret}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ Both Key ID and Secret required!")


if __name__ == "__main__":
    setup_razorpay()
