from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    """Representa um produto disponível para compra."""

    id: int
    name: str
    price: float


class CartItem(BaseModel):
    """Representa um item do carrinho com produto e quantidade."""

    product: Product
    quantity: int


class Coupon(BaseModel):
    """Representa um cupom percentual para o carrinho.

    Attributes:
        code: Código único do cupom.
        discount_percent: Percentual de desconto aplicado no subtotal.
        min_purchase: Valor mínimo de compra para habilitar o cupom.
        is_active: Indica se o cupom está ativo.
        expires_at: Data limite de validade do cupom.
    """

    code: str
    discount_percent: float = Field(gt=0, le=100)
    min_purchase: float = Field(default=0, ge=0)
    is_active: bool = True
    expires_at: Optional[datetime] = None


class CartSummary(BaseModel):
    """Representa a composição final dos totais do carrinho."""

    subtotal: float
    coupon_discount: float
    progressive_discount: float
    total: float
