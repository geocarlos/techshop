"""Testes unitarios do fluxo de checkout."""

from src.checkout import (
    CheckoutItemRequest,
    CheckoutRequest,
    CheckoutService,
    FakePaymentGateway,
    InMemoryPriceCatalog,
    InMemoryStockService,
    PaymentGateway,
    PaymentRequest,
    PaymentResult,
    PricingService,
)


class RejectAllGateway(PaymentGateway):
    """Gateway de pagamento de teste que sempre recusa transacoes."""

    def process(self, request: PaymentRequest) -> PaymentResult:
        """Retorna recusa para qualquer pagamento.

        Args:
            request: Dados de pagamento recebidos.

        Returns:
            PaymentResult: Resultado de pagamento recusado.
        """
        _ = request
        return PaymentResult(approved=False, reason="payment_denied")


def test_process_checkout_success_for_vip_user() -> None:
    """Valida checkout com sucesso para usuario VIP."""
    # Arrange
    request = CheckoutRequest(
        user_id=1,
        is_vip=True,
        items=[CheckoutItemRequest(product_id=10, quantity=2)],
    )
    service = CheckoutService(
        stock_service=InMemoryStockService({10: 5}),
        pricing_service=PricingService(InMemoryPriceCatalog({10: 120.0})),
        payment_gateway=FakePaymentGateway(),
    )

    # Act
    result = service.process_checkout(request)

    # Assert
    assert result.success is True
    assert result.transaction_id is not None
    assert result.total_amount == 217.17


def test_process_checkout_fails_for_insufficient_stock() -> None:
    """Valida falha quando estoque e insuficiente."""
    # Arrange
    request = CheckoutRequest(
        user_id=2,
        is_vip=False,
        items=[CheckoutItemRequest(product_id=7, quantity=3)],
    )
    service = CheckoutService(
        stock_service=InMemoryStockService({7: 1}),
        pricing_service=PricingService(InMemoryPriceCatalog({7: 90.0})),
        payment_gateway=FakePaymentGateway(),
    )

    # Act
    result = service.process_checkout(request)

    # Assert
    assert result.success is False
    assert result.error_code == "stock_unavailable"


def test_process_checkout_fails_for_empty_cart() -> None:
    """Valida falha quando carrinho chega vazio."""
    # Arrange
    request = CheckoutRequest(user_id=3, is_vip=False, items=[])
    service = CheckoutService(
        stock_service=InMemoryStockService({}),
        pricing_service=PricingService(InMemoryPriceCatalog({})),
        payment_gateway=FakePaymentGateway(),
    )

    # Act
    result = service.process_checkout(request)

    # Assert
    assert result.success is False
    assert result.error_code == "cart_empty"


def test_process_checkout_fails_when_gateway_denies_payment() -> None:
    """Valida falha quando o gateway recusa pagamento."""
    # Arrange
    request = CheckoutRequest(
        user_id=4,
        is_vip=False,
        items=[CheckoutItemRequest(product_id=8, quantity=1)],
    )
    service = CheckoutService(
        stock_service=InMemoryStockService({8: 10}),
        pricing_service=PricingService(InMemoryPriceCatalog({8: 150.0})),
        payment_gateway=RejectAllGateway(),
    )

    # Act
    result = service.process_checkout(request)

    # Assert
    assert result.success is False
    assert result.error_code == "payment_denied"
