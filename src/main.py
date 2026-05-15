from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ConfigDict, Field

from src.cart import ShoppingCart
from src.models import CartSummary, Coupon, Product

API_TAGS = [
    {
        "name": "Health",
        "description": "Endpoints para verificacao operacional da API.",
    },
    {
        "name": "Products",
        "description": "Consulta e descoberta de produtos disponiveis.",
    },
    {
        "name": "Cart",
        "description": "Operacoes de carrinho, descontos progressivos e cupons.",
    },
]

ERROR_RESPONSES = {
    400: {"description": "Requisicao invalida ou regra de negocio nao atendida."},
    404: {"description": "Recurso nao encontrado."},
}

app = FastAPI(
    title="TechShop API",
    summary="API de e-commerce para vitrine, carrinho e cupons.",
    description=(
        "Documentacao interativa da API TechShop. Use esta interface Swagger "
        "para testar busca de produtos, resumo de carrinho, adicao/remocao de "
        "itens e aplicacao de cupons."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=API_TAGS,
    swagger_ui_parameters={
        "displayRequestDuration": True,
        "defaultModelsExpandDepth": 1,
        "operationsSorter": "method",
        "tagsSorter": "alpha",
    },
)
cart = ShoppingCart()

static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

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


class ApiStatusResponse(BaseModel):
    """Representa a resposta de saude da API."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "ok"}]},
    )

    status: str = Field(examples=["ok"])


class ProductCatalogItem(BaseModel):
    """Representa um produto retornado pela API de busca."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "iPhone 13 128GB — Meia-noite",
                    "price": 2499.0,
                    "location": "Sao Paulo, SP",
                }
            ]
        },
    )

    id: int = Field(examples=[1])
    name: str = Field(examples=["iPhone 13 128GB — Meia-noite"])
    price: float = Field(ge=0, examples=[2499.0])
    location: str = Field(examples=["Sao Paulo, SP"])


class ApplyCouponRequest(BaseModel):
    """Representa o payload para aplicação de cupom."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"code": "SAVE10"}]},
    )

    code: str = Field(min_length=1, examples=["SAVE10"])


class AddItemRequest(BaseModel):
    """Representa o payload para adicionar item ao carrinho."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"product_id": 1, "quantity": 2}]},
    )

    product_id: int = Field(examples=[1])
    quantity: int = Field(default=1, examples=[2])


APPLY_COUPON_OPENAPI_EXTRA = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": ApplyCouponRequest.model_json_schema(),
                "examples": {
                    "save10": {
                        "summary": "Cupom valido",
                        "value": {"code": "SAVE10"},
                    }
                },
            },
            "application/x-www-form-urlencoded": {
                "schema": {
                    "type": "object",
                    "required": ["coupon_code"],
                    "properties": {
                        "coupon_code": {
                            "type": "string",
                            "example": "SAVE10",
                        }
                    },
                }
            },
        },
    }
}


class CheckoutForm(BaseModel):
    """Representa os dados básicos do checkout."""

    full_name: str
    email: str
    address: str
    payment_method: str


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

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
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

    return render_template(
        "index.html",
        featured_products=featured_products,
        cart_count=len(cart.items),
    )


@app.get("/cart", response_class=HTMLResponse, include_in_schema=False)
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


@app.get("/checkout", response_class=HTMLResponse, include_in_schema=False)
def view_checkout():
    """Renderiza a página de checkout com os dados atuais do carrinho.

    Returns:
        HTML do checkout ou redirecionamento para o carrinho vazio.
    """
    if not cart.items:
        return RedirectResponse(url="/cart", status_code=303)

    summary = cart.calculate_summary()
    return render_template(
        "checkout.html",
        cart_items=cart.items,
        cart_summary=summary,
        cart_count=len(cart.items),
    )


@app.post("/checkout", response_class=HTMLResponse, include_in_schema=False)
async def place_order(request: Request) -> str:
    """Finaliza o checkout, limpa o carrinho e exibe confirmação.

    Args:
        request: Request HTTP com os dados do formulário.

    Raises:
        HTTPException: Se o carrinho estiver vazio ou campos obrigatórios faltarem.

    Returns:
        HTML da confirmação do pedido.
    """
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    form_data = await _parse_request_data(request)
    checkout_form = CheckoutForm(
        full_name=str(form_data.get("full_name", "")).strip(),
        email=str(form_data.get("email", "")).strip(),
        address=str(form_data.get("address", "")).strip(),
        payment_method=str(form_data.get("payment_method", "")).strip(),
    )

    summary = cart.calculate_summary()
    order_id = f"TS-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    cart.items = []
    cart.remove_coupon()

    return render_template(
        "order_confirmation.html",
        order_id=order_id,
        customer_name=checkout_form.full_name,
        cart_summary=summary,
        payment_method=checkout_form.payment_method,
        cart_count=len(cart.items),
    )


@app.get(
    "/api/status",
    response_model=ApiStatusResponse,
    tags=["Health"],
    summary="Verifica status da API",
    response_description="Status operacional da aplicacao.",
)
def api_status() -> ApiStatusResponse:
    """Retorna o status básico da API para fins de compatibilidade.

    Returns:
        Dicionário com status da aplicação.
    """
    return ApiStatusResponse(status="ok")


def _get_product_by_id(product_id: int) -> Product:
    """Retorna um produto da lista de destaque pelo ID.

    Args:
        product_id: Identificador do produto.

    Raises:
        HTTPException: Se produto nao existir.

    Returns:
        Produto encontrado.
    """
    for product in FEATURED_PRODUCTS:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


def _serialize_products(products: list[Product]) -> list[dict[str, Any]]:
    """Serializa produtos para resposta JSON.

    Args:
        products: Lista de produtos.

    Returns:
        Lista serializada com metadados de localizacao.
    """
    payload: list[dict[str, Any]] = []
    for product in products:
        location = ""
        if 1 <= product.id <= len(PRODUCT_LOCATIONS):
            location = PRODUCT_LOCATIONS[product.id - 1]
        payload.append(
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "location": location,
            }
        )
    return payload


async def _parse_request_data(request: Request) -> dict[str, Any]:
    """Extrai dados JSON ou form-urlencoded sem python-multipart.

    Args:
        request: Request HTTP recebida.

    Returns:
        Dicionário com os dados enviados.
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        return await request.json()

    raw_body = await request.body()
    parsed_data = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed_data.items()}


@app.get(
    "/cart/summary",
    response_model=CartSummary,
    tags=["Cart"],
    summary="Consulta resumo do carrinho",
    response_description="Resumo atual com subtotal, descontos e total.",
)
def get_cart_summary() -> CartSummary:
    """Retorna o resumo atual do carrinho com descontos aplicados."""
    return cart.calculate_summary()


@app.post(
    "/cart/add",
    response_model=CartSummary,
    tags=["Cart"],
    summary="Adiciona item ao carrinho",
    response_description="Resumo atualizado apos a inclusao do item.",
    responses=ERROR_RESPONSES,
)
def add_to_cart(request: AddItemRequest) -> CartSummary:
    """Adiciona um item ao carrinho e retorna o resumo atualizado.

    Args:
        request: Payload com produto e quantidade.

    Raises:
        HTTPException: Se quantidade for invalida ou produto nao existir.

    Returns:
        Resumo atualizado do carrinho.
    """
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    product = _get_product_by_id(request.product_id)
    cart.add_item(product=product, quantity=request.quantity)
    return cart.calculate_summary()


@app.delete(
    "/cart/remove/{product_id}",
    response_model=CartSummary,
    tags=["Cart"],
    summary="Remove item do carrinho",
    response_description="Resumo atualizado apos a remocao do item.",
)
def remove_from_cart(product_id: int) -> CartSummary:
    """Remove um item do carrinho e retorna o resumo atualizado.

    Args:
        product_id: ID do produto a remover.

    Returns:
        Resumo atualizado do carrinho.
    """
    cart.remove_item(product_id=product_id)
    return cart.calculate_summary()


@app.post("/cart/remove/{product_id}", include_in_schema=False)
def remove_from_cart_form(product_id: int) -> RedirectResponse:
    """Remove item via formulario HTML e redireciona para /cart.

    Args:
        product_id: ID do produto a remover.

    Returns:
        Redirecionamento para pagina do carrinho.
    """
    cart.remove_item(product_id=product_id)
    return RedirectResponse(url="/cart", status_code=303)


@app.post(
    "/cart/apply-coupon",
    response_model=CartSummary,
    tags=["Cart"],
    summary="Aplica cupom ao carrinho",
    response_description="Resumo atualizado com o cupom aplicado.",
    responses=ERROR_RESPONSES,
    openapi_extra=APPLY_COUPON_OPENAPI_EXTRA,
)
async def apply_coupon(request: Request) -> CartSummary:
    """Aplica um cupom percentual no carrinho atual.

    Args:
        request: Request HTTP com JSON ou form-data contendo o codigo.

    Raises:
        HTTPException: Se cupom não existir ou falhar validação de negócio.

    Returns:
        Resumo atualizado do carrinho.
    """
    request_data = await _parse_request_data(request)
    coupon_code: Optional[str] = str(
        request_data.get("code", request_data.get("coupon_code", ""))
    ).strip().upper()

    if not coupon_code:
        raise HTTPException(status_code=400, detail="Coupon code is required")

    coupon = COUPON_CATALOG.get(coupon_code)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")

    try:
        cart.apply_coupon(coupon)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return cart.calculate_summary()


@app.delete(
    "/cart/coupon",
    response_model=CartSummary,
    tags=["Cart"],
    summary="Remove cupom aplicado",
    response_description="Resumo atualizado sem desconto de cupom.",
)
def remove_coupon() -> CartSummary:
    """Remove o cupom aplicado e retorna o resumo atualizado."""
    cart.remove_coupon()
    return cart.calculate_summary()


@app.get(
    "/api/search",
    response_model=list[ProductCatalogItem],
    tags=["Products"],
    summary="Busca produtos",
    response_description="Produtos encontrados para os filtros informados.",
)
def api_search(q: str = "", category: Optional[str] = None) -> list[dict[str, Any]]:
    """Busca produtos em memoria por termo e categoria.

    Args:
        q: Termo textual de busca.
        category: Categoria opcional (placeholder para filtros futuros).

    Returns:
        Lista de produtos encontrados.
    """
    del category

    normalized_query = q.strip().lower()
    if not normalized_query:
        return _serialize_products(FEATURED_PRODUCTS)

    matched_products = [
        product
        for product in FEATURED_PRODUCTS
        if normalized_query in product.name.lower()
    ]
    return _serialize_products(matched_products)


@app.get("/search", response_class=HTMLResponse, include_in_schema=False)
def search_page(q: str = "") -> str:
    """Renderiza a home com produtos filtrados por termo de busca.

    Args:
        q: Termo textual de busca.

    Returns:
        HTML da home com lista de produtos filtrada.
    """
    normalized_query = q.strip().lower()
    filtered = FEATURED_PRODUCTS
    if normalized_query:
        filtered = [
            product
            for product in FEATURED_PRODUCTS
            if normalized_query in product.name.lower()
        ]

    featured_products = _serialize_products(filtered)
    return render_template(
        "index.html",
        featured_products=featured_products,
        cart_count=len(cart.items),
    )
