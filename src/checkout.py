"""Servicos e modelos do fluxo de checkout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from pydantic import BaseModel, Field


DEFAULT_SHIPPING_FEE = 15.50
DEFAULT_DISCOUNT_THRESHOLD = 200.0
DEFAULT_VIP_DISCOUNT = 0.15
DEFAULT_STANDARD_DISCOUNT = 0.05


class CheckoutItemRequest(BaseModel):
    """Representa um item do checkout recebido pela aplicacao.

    Attributes:
        product_id: Identificador do produto.
        quantity: Quantidade de unidades do produto.
    """

    product_id: int
    quantity: int = Field(gt=0)


class CheckoutRequest(BaseModel):
    """Representa os dados de entrada do checkout.

    Attributes:
        user_id: Identificador do usuario.
        is_vip: Flag que indica se o usuario recebe desconto VIP.
        items: Lista de itens do checkout.
    """

    user_id: int
    is_vip: bool = False
    items: list[CheckoutItemRequest] = Field(default_factory=list)


class PaymentRequest(BaseModel):
    """Representa os dados necessarios para pagamento."""

    user_id: int
    total_amount: float = Field(gt=0)


class PaymentResult(BaseModel):
    """Representa o retorno normalizado da operacao de pagamento."""

    approved: bool
    transaction_id: str | None = None
    reason: str | None = None


class CheckoutResult(BaseModel):
    """Representa o resultado final do checkout."""

    success: bool
    total_amount: float | None = None
    transaction_id: str | None = None
    error_code: str | None = None


class PriceCatalog(Protocol):
    """Contrato para resolucao segura de preco por produto."""

    def get_price(self, product_id: int) -> float:
        """Retorna o preco vigente do produto.

        Args:
            product_id: Identificador do produto.

        Returns:
            float: Preco vigente.

        Raises:
            KeyError: Se o produto nao existir no catalogo.
        """


class StockService(Protocol):
    """Contrato para consulta de estoque."""

    def get_available_stock(self, product_id: int) -> int:
        """Retorna estoque disponivel para o produto."""


class PaymentGateway(Protocol):
    """Contrato para processamento de pagamento."""

    def process(self, request: PaymentRequest) -> PaymentResult:
        """Processa o pagamento e retorna resultado normalizado."""


@dataclass(frozen=True)
class PricingPolicy:
    """Define politicas de precificacao aplicadas ao checkout.

    Attributes:
        shipping_fee: Valor fixo de frete.
        discount_threshold: Limiar minimo para aplicar desconto.
        vip_discount_rate: Percentual de desconto VIP.
        standard_discount_rate: Percentual de desconto padrao.
    """

    shipping_fee: float = DEFAULT_SHIPPING_FEE
    discount_threshold: float = DEFAULT_DISCOUNT_THRESHOLD
    vip_discount_rate: float = DEFAULT_VIP_DISCOUNT
    standard_discount_rate: float = DEFAULT_STANDARD_DISCOUNT


class PricingService:
    """Calcula subtotal e total final com base no catalogo e politica."""

    def __init__(self, catalog: PriceCatalog, policy: PricingPolicy | None = None) -> None:
        """Inicializa o servico de precificacao.

        Args:
            catalog: Fonte confiavel de precos dos produtos.
            policy: Politica de frete e desconto.
        """
        self._catalog = catalog
        self._policy = policy or PricingPolicy()

    def calculate_subtotal(self, items: list[CheckoutItemRequest]) -> float:
        """Calcula subtotal com preco resolvido no servidor.

        Args:
            items: Itens do checkout.

        Returns:
            float: Subtotal sem frete e desconto.
        """
        subtotal = 0.0
        for item in items:
            unit_price = self._catalog.get_price(item.product_id)
            subtotal += unit_price * item.quantity
        return subtotal

    def calculate_total(self, subtotal: float, is_vip: bool) -> float:
        """Calcula total aplicando frete e desconto.

        Args:
            subtotal: Valor total dos itens.
            is_vip: Flag de desconto VIP.

        Returns:
            float: Total final arredondado em duas casas.
        """
        total = subtotal + self._policy.shipping_fee
        if total > self._policy.discount_threshold:
            discount_rate = (
                self._policy.vip_discount_rate if is_vip else self._policy.standard_discount_rate
            )
            total *= 1.0 - discount_rate
        return round(total, 2)


class CheckoutService:
    """Orquestra o fluxo de checkout de forma coesa e tipada."""

    def __init__(
        self,
        stock_service: StockService,
        pricing_service: PricingService,
        payment_gateway: PaymentGateway,
    ) -> None:
        """Inicializa o servico de checkout.

        Args:
            stock_service: Servico para validacao de estoque.
            pricing_service: Servico para calculo de total.
            payment_gateway: Gateway para processamento de pagamento.
        """
        self._stock_service = stock_service
        self._pricing_service = pricing_service
        self._payment_gateway = payment_gateway

    def process_checkout(self, request: CheckoutRequest) -> CheckoutResult:
        """Processa checkout com validacao de estoque e pagamento.

        Args:
            request: Dados de entrada do checkout.

        Returns:
            CheckoutResult: Resultado do checkout.
        """
        if not request.items:
            return CheckoutResult(success=False, error_code="cart_empty")

        for item in request.items:
            available_stock = self._stock_service.get_available_stock(item.product_id)
            if item.quantity > available_stock:
                return CheckoutResult(success=False, error_code="stock_unavailable")

        subtotal = self._pricing_service.calculate_subtotal(request.items)
        if subtotal <= 0:
            return CheckoutResult(success=False, error_code="invalid_cart_total")

        total_amount = self._pricing_service.calculate_total(subtotal, request.is_vip)
        payment_result = self._payment_gateway.process(
            PaymentRequest(user_id=request.user_id, total_amount=total_amount)
        )
        if not payment_result.approved:
            return CheckoutResult(success=False, error_code=payment_result.reason or "payment_denied")

        return CheckoutResult(
            success=True,
            total_amount=total_amount,
            transaction_id=payment_result.transaction_id,
        )


class InMemoryPriceCatalog:
    """Catalogo em memoria para ambientes de desenvolvimento e teste."""

    def __init__(self, prices_by_product_id: Mapping[int, float]) -> None:
        """Inicializa o catalogo com precos por produto.

        Args:
            prices_by_product_id: Mapa de identificador para preco unitario.
        """
        self._prices = dict(prices_by_product_id)

    def get_price(self, product_id: int) -> float:
        """Retorna preco de produto do catalogo em memoria."""
        return self._prices[product_id]


class InMemoryStockService:
    """Servico de estoque em memoria para ambientes de desenvolvimento e teste."""

    def __init__(self, stock_by_product_id: Mapping[int, int]) -> None:
        """Inicializa mapa de estoque por produto.

        Args:
            stock_by_product_id: Quantidade disponivel por identificador de produto.
        """
        self._stock = dict(stock_by_product_id)

    def get_available_stock(self, product_id: int) -> int:
        """Retorna estoque disponivel do produto informado."""
        return self._stock.get(product_id, 0)


class FakePaymentGateway:
    """Gateway de pagamento simulado sem exposicao de dados sensiveis."""

    def process(self, request: PaymentRequest) -> PaymentResult:
        """Aprova valores validos e recusa valores fora de faixa.

        Args:
            request: Dados de pagamento normalizados.

        Returns:
            PaymentResult: Resultado de aprovacao ou recusa.
        """
        if 0 < request.total_amount < 9999:
            return PaymentResult(approved=True, transaction_id="txn_simulada_123")
        return PaymentResult(approved=False, reason="invalid_amount")


def processar_tudo(
    cart_data: Mapping[str, Any],
    u_data: Mapping[str, Any],
    *,
    catalog_prices: Mapping[int, float],
    stock_by_product: Mapping[int, int] | None = None,
    payment_gateway: PaymentGateway | None = None,
) -> dict[str, Any]:
    """Mantem compatibilidade com o formato legado de entrada.

    Esta funcao existe para reduzir impacto de migracao e converte dicionarios
    para contratos tipados antes de delegar para ``CheckoutService``.

    Args:
        cart_data: Estrutura legada com chave ``items``.
        u_data: Estrutura legada contendo ``id`` e opcionalmente ``vip``.
        catalog_prices: Fonte confiavel de preco por produto.
        stock_by_product: Estoque por produto. Se ausente, usa 10 para cada item.
        payment_gateway: Gateway de pagamento customizado para testes/integracao.

    Returns:
        dict[str, Any]: Resultado legivel para chamadas legadas.
    """
    items_data = cart_data.get("items", [])
    items: list[CheckoutItemRequest] = []
    for item in items_data:
        items.append(CheckoutItemRequest(product_id=int(item["id"]), quantity=int(item["qtd"])))

    stock_map = stock_by_product or {item.product_id: 10 for item in items}
    checkout_request = CheckoutRequest(
        user_id=int(u_data["id"]),
        is_vip=bool(u_data.get("vip", False)),
        items=items,
    )

    checkout_service = CheckoutService(
        stock_service=InMemoryStockService(stock_map),
        pricing_service=PricingService(InMemoryPriceCatalog(catalog_prices)),
        payment_gateway=payment_gateway or FakePaymentGateway(),
    )
    result = checkout_service.process_checkout(checkout_request)

    if result.success:
        return {
            "sucesso": True,
            "transacao": result.transaction_id,
            "valor_total": result.total_amount,
        }

    return {
        "sucesso": False,
        "erro": result.error_code,
    }
