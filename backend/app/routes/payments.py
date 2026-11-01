import json
from typing import List
from fastapi import APIRouter, Depends, Request, Header, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.dependencies.auth import get_current_user
from backend.app.models.user import AppUser
from backend.app.schemas.payment import (
    OrderCreateRequest, OrderCreateResponse, PaymentVerifyRequest,
    CashPaymentConfirmRequest, PaymentOut
)
from backend.app.services.payment_service import (
    create_payment_order, verify_razorpay_payment,
    confirm_cash_payment, get_payment_history
)

router = APIRouter(prefix="/payments", tags=["Payment Gateway"])


@router.post("/create-order", response_model=OrderCreateResponse)
def create_order(
    data: OrderCreateRequest,
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_payment_order(db, data.loan_id, current_user, data.payment_type)


@router.post("/verify", response_model=PaymentOut)
def verify_payment(
    data: PaymentVerifyRequest,
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return verify_razorpay_payment(db, data, current_user)


@router.post("/cash-confirm", response_model=PaymentOut)
def confirm_cash(
    data: CashPaymentConfirmRequest,
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return confirm_cash_payment(db, data.payment_id, current_user)


@router.get("/history", response_model=List[PaymentOut])
def payment_history(
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_payment_history(db, current_user)


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    raw_body = await request.body()
    # Webhook signature verification
    import hmac, hashlib
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    expected_sig = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

    if expected_sig != x_razorpay_signature and settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature.")

    try:
        payload = json.loads(raw_body.decode())
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload.")

    event_type = payload.get("event")
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})

    return {"status": "ok", "event": event_type}
