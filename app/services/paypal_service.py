import requests
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class PayPalService:
    def __init__(self):
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', 'your_paypal_client_id')
        self.client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', 'your_paypal_client_secret')
        self.base_url = getattr(settings, 'PAYPAL_BASE_URL', 'https://api-m.sandbox.paypal.com')  # Use sandbox for testing
        self.access_token = None
        self.token_expires_at = None

    def get_access_token(self) -> str:
        """Get or refresh PayPal access token"""
        if self.access_token and self.token_expires_at and datetime.utcnow() < self.token_expires_at:
            return self.access_token

        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = 'grant_type=client_credentials'

        try:
            response = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)  # Default to 1 hour
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)  # Refresh 1 minute early
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get PayPal access token: {e}")
            raise Exception(f"PayPal authentication failed: {e}")

    def create_product(self, plan_name: str, description: str) -> str:
        """Create a PayPal product for subscription"""
        access_token = self.get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'PayPal-Request-Id': f'product-{plan_name}-{int(datetime.utcnow().timestamp())}'
        }

        product_data = {
            'name': f'Real Estate Platform - {plan_name}',
            'description': description,
            'type': 'SERVICE',
            'category': 'SOFTWARE'
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/catalogs/products",
                headers=headers,
                json=product_data
            )
            response.raise_for_status()
            
            product = response.json()
            return product['id']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create PayPal product: {e}")
            raise Exception(f"PayPal product creation failed: {e}")

    def create_billing_plan(self, product_id: str, plan_name: str, price: float, billing_cycle: str = 'monthly') -> str:
        """Create a PayPal billing plan"""
        access_token = self.get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'PayPal-Request-Id': f'plan-{plan_name}-{int(datetime.utcnow().timestamp())}'
        }

        # Set billing cycle details
        if billing_cycle == 'monthly':
            interval_unit = 'MONTH'
            interval_count = 1
        else:  # annual
            interval_unit = 'YEAR'
            interval_count = 1

        plan_data = {
            'product_id': product_id,
            'name': f'{plan_name.title()} Plan - {billing_cycle.title()}',
            'description': f'Real Estate Platform {plan_name.title()} subscription - {billing_cycle} billing',
            'status': 'ACTIVE',
            'billing_cycles': [
                {
                    'frequency': {
                        'interval_unit': interval_unit,
                        'interval_count': interval_count
                    },
                    'tenure_type': 'REGULAR',
                    'sequence': 1,
                    'total_cycles': 0,  # Infinite cycles
                    'pricing_scheme': {
                        'fixed_price': {
                            'value': str(price),
                            'currency_code': 'USD'
                        }
                    }
                }
            ],
            'payment_preferences': {
                'auto_bill_outstanding': True,
                'setup_fee': {
                    'value': '0',
                    'currency_code': 'USD'
                },
                'setup_fee_failure_action': 'CONTINUE',
                'payment_failure_threshold': 3
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/billing/plans",
                headers=headers,
                json=plan_data
            )
            response.raise_for_status()
            
            plan = response.json()
            return plan['id']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create PayPal billing plan: {e}")
            raise Exception(f"PayPal billing plan creation failed: {e}")

    def create_subscription(self, plan_id: str, subscriber_email: str, subscriber_name: str) -> Dict[str, Any]:
        """Create a PayPal subscription"""
        access_token = self.get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'PayPal-Request-Id': f'subscription-{int(datetime.utcnow().timestamp())}'
        }

        subscription_data = {
            'plan_id': plan_id,
            'start_time': (datetime.utcnow() + timedelta(minutes=5)).isoformat() + 'Z',  # Start in 5 minutes
            'subscriber': {
                'name': {
                    'given_name': subscriber_name.split()[0] if subscriber_name else 'User',
                    'surname': ' '.join(subscriber_name.split()[1:]) if len(subscriber_name.split()) > 1 else 'User'
                },
                'email_address': subscriber_email
            },
            'application_context': {
                'brand_name': 'Real Estate Platform',
                'locale': 'en-US',
                'shipping_preference': 'NO_SHIPPING',
                'user_action': 'SUBSCRIBE_NOW',
                'payment_method': {
                    'payer_selected': 'PAYPAL',
                    'payee_preferred': 'IMMEDIATE_PAYMENT_REQUIRED'
                },
                'return_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/subscription/success",
                'cancel_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/subscription/cancel"
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/billing/subscriptions",
                headers=headers,
                json=subscription_data
            )
            response.raise_for_status()
            
            subscription = response.json()
            return subscription
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create PayPal subscription: {e}")
            raise Exception(f"PayPal subscription creation failed: {e}")

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get PayPal subscription details"""
        access_token = self.get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}",
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get PayPal subscription: {e}")
            raise Exception(f"PayPal subscription retrieval failed: {e}")

    def cancel_subscription(self, subscription_id: str, reason: str = "User requested cancellation") -> bool:
        """Cancel a PayPal subscription"""
        access_token = self.get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        cancel_data = {
            'reason': reason
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel",
                headers=headers,
                json=cancel_data
            )
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to cancel PayPal subscription: {e}")
            raise Exception(f"PayPal subscription cancellation failed: {e}")

    def verify_webhook_signature(self, headers: Dict[str, str], body: str) -> bool:
        """Verify PayPal webhook signature"""
        # TODO: Implement proper webhook signature verification
        # This is a simplified version - in production, you should verify the signature
        # using PayPal's webhook verification API
        
        auth_algo = headers.get('PAYPAL-AUTH-ALGO')
        transmission_id = headers.get('PAYPAL-TRANSMISSION-ID')
        cert_id = headers.get('PAYPAL-CERT-ID')
        transmission_sig = headers.get('PAYPAL-TRANSMISSION-SIG')
        transmission_time = headers.get('PAYPAL-TRANSMISSION-TIME')
        
        # For now, just check if required headers are present
        required_headers = [auth_algo, transmission_id, cert_id, transmission_sig, transmission_time]
        return all(header is not None for header in required_headers)

# Global PayPal service instance
paypal_service = PayPalService()
