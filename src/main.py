from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from src.cart import ShoppingCart
from src.models import CartSummary, Coupon, Product

app = FastAPI()
cart = ShoppingCart()

# Configurar Jinja2
templates_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))


def render_template(template_name: str, **context) -> str:
    """Renderiza um template Jinja2 com o contexto fornecido.

    Args:
        template_name: Nome do arquivo template (ex: "index.html").
        **context: Variáveis para passar ao template.

    Returns:
        String HTML renderizada.
    """
    template = jinja_env.get_template(template_name)
    return template.render(**context)


# Dados mockados para demonstração
FEATURED_PRODUCTS = [
    Product(id=1, name="iPhone 13 128GB — Meia-noite", price=2499.00),
    Product(id=2, name="MacBook Air M1 8GB 256GB", price=5800.00),
    Product(id=3, name="PlayStation 5 + 2 Controles", price=3200.00),
    Product(id=4, name="Samsung Galaxy Tab S7 — 128GB", price=1850.00),
    Product(id=5, name="Sony WH-1000XM5 — Noise Cancelling", price=1100.00),
    Product(id=6, name="Canon EOS R50 + Lente 18-45mm", price=4300.00),
]

PRODUCT_LOCATIONS = [
    "São Paulo, SP",
    "Curitiba, PR",
    "Rio de Janeiro, RJ",
    "Belo Horizonte, MG",
    "Porto Alegre, RS",
    "Recife, PE",
]


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

@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """Renderiza a página inicial com produtos em destaque.

    Returns:
        HTML da página home renderizada com Jinja2.
    """
    featured_products = [
        {
            "id": i,
            "name": FEATURED_PRODUCTS[i].name,
            "price": FEATURED_PRODUCTS[i].price,
            "location": PRODUCT_LOCATIONS[i],
        }
        for i in range(len(FEATURED_PRODUCTS))
    ]

    return render_template("index.html", featured_products=featured_products, cart_count=len(cart.items))


@app.get("/cart", response_class=HTMLResponse)
def view_cart() -> str:
    """Renderiza a página do carrinho com resumo de totais.

    Returns:
        HTML do carrinho renderizado com Jinja2.
    """
    summary = cart.calculate_summary()
    return render_template(
        "cart.html",
        cart_items=cart.items,
        cart_summary=summary,
        cart_count=len(cart.items),
    )


@app.get("/api/status")
def api_status() -> dict[str, str]:
    """Retorna o status básico da API para fins de compatibilidade.

    Returns:
        Dicionário com status da aplicação.
    """
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
