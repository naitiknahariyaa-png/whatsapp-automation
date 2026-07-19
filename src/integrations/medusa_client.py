"""
Medusa Integration - Open Source Commerce Engine
===============================================
Build online stores with ease

Based on: https://github.com/medusajs/medusa

Features:
- E-commerce functionality
- Product management
- Order processing
- Payment integration
- Shipping management
- 100% FREE!

Setup:
    npm install -g @medusajs/medusa-cli
    medusa init
    medusa start
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class MedusaClient:
    """
    Medusa Commerce Client
    
    Use Cases:
    - E-commerce store
    - Product catalog
    - Order management
    - Multi-vendor marketplace
    - Subscription commerce
    
    Setup:
    1. Install:
       npm install -g @medusajs/medusa-cli
       medusa init my-store
       cd my-store
       npm start
    
    2. Or use Docker:
       docker run -d -p 9000:9000 \\
         -e MEDUSA_ADMIN_PORT=7000 \\
         medusajs/medusa
    
    Environment:
    - MEDUSA_URL=http://localhost:9000
    - MEDUSA_API_KEY=your-api-key
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.url = url or os.getenv("MEDUSA_URL", "http://localhost:9000")
        self.api_key = api_key or os.getenv("MEDUSA_API_KEY", "")
        self.enabled = bool(self.url)
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        
        if self.enabled:
            logger.info(f"✅ Medusa configured: {self.url}")
        else:
            logger.warning("⚠️ Medusa not configured")
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make API request"""
        try:
            response = requests.request(
                method,
                f"{self.url}/store{endpoint}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            if response.status_code < 400:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Medusa error: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════
    # PRODUCTS
    # ═══════════════════════════════════════════════════════════════
    
    def list_products(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """List all products"""
        result = self._request(
            "GET",
            f"/products?limit={limit}&offset={offset}"
        )
        return result.get("products", []) if result else []
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Get single product"""
        return self._request("GET", f"/products/{product_id}")
    
    def search_products(self, query: str) -> List[Dict]:
        """Search products"""
        result = self._request(
            "GET",
            f"/products?q={query}"
        )
        return result.get("products", []) if result else []
    
    # ═══════════════════════════════════════════════════════════════
    # ORDERS
    # ═══════════════════════════════════════════════════════════════
    
    def create_order(
        self,
        email: str,
        items: List[Dict],
        shipping_address: Dict,
        customer_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create new order
        
        Args:
            email: Customer email
            items: [{"variant_id": "xxx", "quantity": 2}]
            shipping_address: {address_1, city, country_code}
        """
        data = {
            "email": email,
            "items": items,
            "shipping_address": shipping_address
        }
        if customer_id:
            data["customer_id"] = customer_id
        
        return self._request("POST", "/orders", data)
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order details"""
        return self._request("GET", f"/orders/{order_id}")
    
    def list_orders(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """List all orders"""
        result = self._request(
            "GET",
            f"/orders?limit={limit}&offset={offset}"
        )
        return result.get("orders", []) if result else []
    
    # ═══════════════════════════════════════════════════════════════
    # CUSTOMERS
    # ═══════════════════════════════════════════════════════════════
    
    def create_customer(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        phone: str = ""
    ) -> Optional[Dict]:
        """Create customer"""
        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone
        }
        return self._request("POST", "/customers", data)
    
    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Get customer details"""
        return self._request("GET", f"/customers/{customer_id}")
    
    # ═══════════════════════════════════════════════════════════════
    # CART
    # ═══════════════════════════════════════════════════════════════
    
    def create_cart(
        self,
        region_id: str = "reg_xxx"
    ) -> Optional[Dict]:
        """Create new cart"""
        return self._request("POST", "/carts", {"region_id": region_id})
    
    def add_to_cart(
        self,
        cart_id: str,
        variant_id: str,
        quantity: int = 1
    ) -> Optional[Dict]:
        """Add item to cart"""
        return self._request(
            "POST",
            f"/carts/{cart_id}/line-items",
            {"variant_id": variant_id, "quantity": quantity}
        )
    
    # ═══════════════════════════════════════════════════════════════
    # REGIONS & SHIPPING
    # ═══════════════════════════════════════════════════════════════
    
    def list_regions(self) -> List[Dict]:
        """List shipping regions"""
        result = self._request("GET", "/regions")
        return result.get("regions", []) if result else []
    
    def list_shipping_options(self, region_id: str) -> List[Dict]:
        """Get shipping options for region"""
        result = self._request("GET", f"/regions/{region_id}/shipping-options")
        return result.get("shipping_options", []) if result else []


def setup_medusa():
    """Setup guide for Medusa"""
    print("\n" + "="*50)
    print("🛒 Medusa Commerce Setup")
    print("="*50 + "\n")
    
    print("Installation:")
    print("-" * 40)
    print("1. Install Node.js (v18+)")
    print("2. npm install -g @medusajs/medusa-cli")
    print("3. medusa init my-store")
    print("4. cd my-store")
    print("5. medusa develop")
    print("\nDocker (Alternative):")
    print("docker run -d -p 9000:9000 medusajs/medusa\n")
    
    url = input("Medusa URL (press Enter for default): ").strip()
    if not url:
        url = "http://localhost:9000"
    
    key = input("API Key (optional): ").strip()
    
    with open(".env", "a") as f:
        f.write(f"\n# Medusa (E-commerce)\n")
        f.write(f"MEDUSA_URL={url}\n")
        if key:
            f.write(f"MEDUSA_API_KEY={key}\n")
    print("✅ Saved to .env!")


if __name__ == "__main__":
    setup_medusa()
