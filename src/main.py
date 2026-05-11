from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.cart import ShoppingCart
from src.models import CartSummary, Coupon

app = FastAPI()
cart = ShoppingCart()


class ApplyCouponRequest(BaseModel):
    """Representa o payload para aplicação de cupom."""

    code: str


COUPON_CATALOG: dict[str, Coupon] = {
    "SAVE10": Coupon(code="SAVE10", discount_percent=10, min_purchase=100),
    "VIP15": Coupon(
        code="VIP15",
        discount_percent=15,
        min_purchase=300,
        expires_at=datetime.now() + timedelta(days=30),
    ),
    "INACTIVE5": Coupon(code="INACTIVE5", discount_percent=5, is_active=False),
}

@app.get("/")
def read_root():
    """Retorna o status básico da API."""
    return {"status": "ok"}


@app.get("/cart/summary", response_model=CartSummary)
def get_cart_summary() -> CartSummary:
    """Retorna o resumo atual do carrinho com descontos aplicados."""
    return cart.calculate_summary()


@app.post("/cart/apply-coupon", response_model=CartSummary)
def apply_coupon(request: ApplyCouponRequest) -> CartSummary:
    """Aplica um cupom percentual no carrinho atual.

    Args:
        request: Payload com o código do cupom.

    Raises:
        HTTPException: Se cupom não existir ou falhar validação de negócio.

    Returns:
        Resumo atualizado do carrinho.
    """
    coupon_code = request.code.strip().upper()
    coupon = COUPON_CATALOG.get(coupon_code)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")

    try:
        cart.apply_coupon(coupon)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return cart.calculate_summary()


@app.delete("/cart/coupon", response_model=CartSummary)
def remove_coupon() -> CartSummary:
    """Remove o cupom aplicado e retorna o resumo atualizado."""
    cart.remove_coupon()
    return cart.calculate_summary()
