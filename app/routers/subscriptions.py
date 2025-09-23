from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import stripe
import logging

from app.database import get_db
from app.models import User, Subscription, UserRole, SubscriptionPlan
from app.schemas import SubscriptionCreate, SubscriptionResponse
from app.routers.auth import get_current_user, require_agent
from app.core.config import settings
from app.services.paypal_service import paypal_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic Plan",
        "price": 49.00,
        "features": [
            "Unlimited property listings",
            "Standard visibility",
            "Basic lead access",
            "Email support"
        ],
        "limits": {
            "listings": None,  # Unlimited
            "featured_listings": 0,
            "analytics_views": 100
        }
    },
    "pro": {
        "name": "Pro Plan",
        "price": 99.00,
        "features": [
            "Unlimited property listings",
            "Featured listings (priority placement)",
            "Advanced analytics (views, clicks, leads)",
            "Access to verified buyer leads",
            "Priority email support"
        ],
        "limits": {
            "listings": None,  # Unlimited
            "featured_listings": 5,
            "analytics_views": 1000
        }
    },
    "premium": {
        "name": "Premium Plan",
        "price": 199.00,
        "features": [
            "All Pro features",
            "Banner placement on homepage",
            "Exclusive leads (priority notifications)",
            "Dedicated account manager",
            "Phone support"
        ],
        "limits": {
            "listings": None,  # Unlimited
            "featured_listings": 20,
            "analytics_views": None  # Unlimited
        }
    }
}

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "billing_cycles": ["monthly", "annual"],
        "annual_discount": 0.15  # 15% discount for annual billing
    }

@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    plan_name: str,
    billing_cycle: str = "monthly",
    payment_method: str = "stripe",
    payment_token: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent)
):
    """Create a new subscription for an agent"""
    
    # Validate plan
    if plan_name not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Available plans: {list(SUBSCRIPTION_PLANS.keys())}"
        )
    
    # Validate billing cycle
    if billing_cycle not in ["monthly", "annual"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Billing cycle must be 'monthly' or 'annual'"
        )
    
    # Check if user already has an active subscription
    existing_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active subscription. Please cancel it first."
        )
    
    plan_config = SUBSCRIPTION_PLANS[plan_name]
    base_price = plan_config["price"]
    
    # Apply annual discount
    if billing_cycle == "annual":
        final_price = base_price * 12 * 0.85  # 15% discount
    else:
        final_price = base_price
    
    try:
        if payment_method == "stripe":
            # Create Stripe customer if not exists
            if not current_user.stripe_customer_id:
                stripe_customer = stripe.Customer.create(
                    email=current_user.email,
                    name=f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else current_user.username
                )
                current_user.stripe_customer_id = stripe_customer.id
                db.commit()
            
            # Create Stripe subscription
            stripe_subscription = stripe.Subscription.create(
                customer=current_user.stripe_customer_id,
                items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{plan_config['name']} - {billing_cycle.title()}",
                        },
                        'unit_amount': int(final_price * 100),  # Stripe uses cents
                        'recurring': {
                            'interval': 'month' if billing_cycle == 'monthly' else 'year',
                        },
                    },
                }],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )
            
            payment_id = stripe_subscription.latest_invoice.payment_intent.id
            subscription_id = stripe_subscription.id
            
        elif payment_method == "paypal":
            # Create PayPal product and billing plan
            try:
                product_id = paypal_service.create_product(
                    plan_name,
                    plan_config["name"]
                )

                plan_id = paypal_service.create_billing_plan(
                    product_id,
                    plan_name,
                    final_price,
                    billing_cycle
                )

                # Create PayPal subscription
                paypal_subscription = paypal_service.create_subscription(
                    plan_id,
                    current_user.email,
                    f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else current_user.username
                )

                payment_id = paypal_subscription['id']
                subscription_id = paypal_subscription['id']

                # Return approval URL for frontend to redirect user
                approval_url = None
                for link in paypal_subscription.get('links', []):
                    if link['rel'] == 'approve':
                        approval_url = link['href']
                        break

                if not approval_url:
                    raise Exception("No approval URL found in PayPal response")

            except Exception as e:
                logger.error(f"PayPal subscription creation failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PayPal subscription creation failed: {str(e)}"
                )
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment method. Supported: stripe, paypal"
            )
        
        # Create subscription record
        current_period_start = datetime.utcnow()
        if billing_cycle == "monthly":
            current_period_end = current_period_start + timedelta(days=30)
        else:
            current_period_end = current_period_start + timedelta(days=365)
        
        db_subscription = Subscription(
            user_id=current_user.id,
            plan_name=plan_name,
            plan_price=final_price,
            billing_cycle=billing_cycle,
            payment_method=payment_method,
            payment_id=payment_id,
            subscription_id=subscription_id,
            status="active",
            current_period_start=current_period_start,
            current_period_end=current_period_end
        )
        
        db.add(db_subscription)
        
        # Update user subscription status
        current_user.subscription_plan = SubscriptionPlan(plan_name.upper())
        current_user.subscription_status = "active"
        current_user.subscription_expires_at = current_period_end
        
        db.commit()
        db.refresh(db_subscription)
        
        return db_subscription
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Subscription creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating subscription"
        )

@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent)
):
    """Get current user's active subscription"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription

@router.put("/cancel")
async def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent)
):
    """Cancel current subscription"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    try:
        if subscription.payment_method == "stripe":
            # Cancel Stripe subscription
            stripe.Subscription.delete(subscription.subscription_id)
        
        # Update subscription status
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()
        
        # Update user status
        current_user.subscription_status = "cancelled"
        
        db.commit()
        
        return {"message": "Subscription cancelled successfully"}
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe cancellation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error cancelling subscription: {str(e)}"
        )

@router.get("/usage")
async def get_subscription_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent)
):
    """Get current subscription usage statistics"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    plan_limits = SUBSCRIPTION_PLANS[subscription.plan_name]["limits"]
    
    usage_stats = {
        "plan_name": subscription.plan_name,
        "billing_cycle": subscription.billing_cycle,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "usage": {
            "listings_used": subscription.listings_used,
            "featured_listings_used": subscription.featured_listings_used,
            "analytics_views": subscription.analytics_views
        },
        "limits": plan_limits,
        "usage_percentage": {
            "featured_listings": (subscription.featured_listings_used / plan_limits["featured_listings"] * 100) if plan_limits["featured_listings"] else 0,
            "analytics_views": (subscription.analytics_views / plan_limits["analytics_views"] * 100) if plan_limits["analytics_views"] else 0
        }
    }
    
    return usage_stats

@router.post("/upgrade")
async def upgrade_subscription(
    new_plan: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent)
):
    """Upgrade current subscription to a higher plan"""
    
    if new_plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Available plans: {list(SUBSCRIPTION_PLANS.keys())}"
        )
    
    current_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not current_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # Validate upgrade (can only upgrade to higher tier)
    plan_hierarchy = {"basic": 1, "pro": 2, "premium": 3}
    current_tier = plan_hierarchy[current_subscription.plan_name]
    new_tier = plan_hierarchy[new_plan]
    
    if new_tier <= current_tier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only upgrade to a higher tier plan"
        )
    
    try:
        # Calculate prorated amount
        new_plan_config = SUBSCRIPTION_PLANS[new_plan]
        new_price = new_plan_config["price"]
        
        if current_subscription.billing_cycle == "annual":
            new_price *= 12 * 0.85  # Apply annual discount
        
        # Update subscription
        current_subscription.plan_name = new_plan
        current_subscription.plan_price = new_price
        
        # Update user
        current_user.subscription_plan = SubscriptionPlan(new_plan.upper())
        
        db.commit()
        
        return {
            "message": f"Successfully upgraded to {new_plan_config['name']}",
            "new_plan": new_plan,
            "new_price": new_price
        }
        
    except Exception as e:
        logger.error(f"Subscription upgrade error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error upgrading subscription"
        )

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, getattr(settings, 'STRIPE_WEBHOOK_SECRET', 'whsec_...')
        )
    except ValueError:
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        # Payment succeeded - activate/renew subscription
        invoice = event['data']['object']
        subscription_id = invoice['subscription']

        # Find subscription in database
        subscription = db.query(Subscription).filter(
            Subscription.subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = "active"
            subscription.current_period_start = datetime.fromtimestamp(invoice['period_start'])
            subscription.current_period_end = datetime.fromtimestamp(invoice['period_end'])

            # Update user status
            user = db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                user.subscription_status = "active"
                user.subscription_expires_at = subscription.current_period_end

            db.commit()
            logger.info(f"Subscription {subscription_id} activated/renewed")

    elif event['type'] == 'invoice.payment_failed':
        # Payment failed - mark subscription as past due
        invoice = event['data']['object']
        subscription_id = invoice['subscription']

        subscription = db.query(Subscription).filter(
            Subscription.subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = "past_due"

            # Update user status
            user = db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                user.subscription_status = "past_due"

            db.commit()
            logger.info(f"Subscription {subscription_id} marked as past due")

    elif event['type'] == 'customer.subscription.deleted':
        # Subscription cancelled
        subscription_obj = event['data']['object']
        subscription_id = subscription_obj['id']

        subscription = db.query(Subscription).filter(
            Subscription.subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = "cancelled"

            # Update user status
            user = db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                user.subscription_status = "cancelled"
                user.subscription_plan = SubscriptionPlan.FREE

            db.commit()
            logger.info(f"Subscription {subscription_id} cancelled")

    return {"status": "success"}

@router.post("/webhooks/paypal")
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle PayPal webhook events"""
    payload = await request.json()
    headers = dict(request.headers)

    # Verify webhook signature
    body = await request.body()
    if not paypal_service.verify_webhook_signature(headers, body.decode()):
        logger.warning("PayPal webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    logger.info(f"PayPal webhook received: {payload.get('event_type')}")

    event_type = payload.get('event_type')

    if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
        # Subscription activated
        subscription_id = payload['resource']['id']

        subscription = db.query(Subscription).filter(
            Subscription.subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = "active"

            # Update user status
            user = db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                user.subscription_status = "active"

            db.commit()
            logger.info(f"PayPal subscription {subscription_id} activated")

    elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
        # Subscription cancelled
        subscription_id = payload['resource']['id']

        subscription = db.query(Subscription).filter(
            Subscription.subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = "cancelled"

            # Update user status
            user = db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                user.subscription_status = "cancelled"
                user.subscription_plan = SubscriptionPlan.FREE

            db.commit()
            logger.info(f"PayPal subscription {subscription_id} cancelled")

    return {"status": "success"}
