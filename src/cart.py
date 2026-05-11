from datetime import datetime
from typing import List, Optional

from src.models import CartItem, CartSummary, Coupon, Product

class ShoppingCart:
    """
    Representa um carrinho de compras.
    """
    def __init__(self):
        """
        Inicializa um carrinho de compras com uma lista vazia de itens.
        """
        self.items: List[CartItem] = []
        self.coupon: Optional[Coupon] = None

    def add_item(self, product: Product, quantity: int):
        """
        Adiciona um produto ao carrinho. Se o produto já existir,
        a quantidade é somada à existente.

        Args:
            product (Product): O produto a ser adicionado.
            quantity (int): A quantidade a ser adicionada.
        """
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return

        self.items.append(CartItem(product=product, quantity=quantity))

    def remove_item(self, product_id: int):
        """
        Remove um item do carrinho pelo ID do produto.

        Args:
            product_id (int): O ID do produto a ser removido.
        """
        self.items = [item for item in self.items if item.product.id != product_id]

    def calculate_total(self) -> float:
        """
        Calcula o valor total dos itens no carrinho.

        Returns:
            float: O valor total do carrinho.
        """
        return sum(item.product.price * item.quantity for item in self.items)

    def apply_coupon(self, coupon: Coupon, reference_datetime: Optional[datetime] = None) -> None:
        """Aplica um cupom no carrinho após validações de negócio.

        Args:
            coupon: Cupom percentual a ser aplicado.
            reference_datetime: Data/hora de referência para validar expiração.

        Raises:
            ValueError: Se o cupom estiver inativo, expirado ou abaixo da compra mínima.
        """
        current_datetime = reference_datetime or datetime.now()
        subtotal = self.calculate_total()

        if not coupon.is_active:
            raise ValueError("Coupon is inactive")

        if coupon.expires_at is not None and current_datetime > coupon.expires_at:
            raise ValueError("Coupon is expired")

        if subtotal < coupon.min_purchase:
            raise ValueError("Cart subtotal is below coupon minimum purchase")

        self.coupon = coupon

    def remove_coupon(self) -> None:
        """Remove o cupom atualmente aplicado no carrinho."""
        self.coupon = None

    def _calculate_progressive_discount(self, total: float) -> float:
        """Calcula desconto progressivo com base no total informado.

        Args:
            total: Valor sobre o qual o desconto progressivo deve ser aplicado.

        Returns:
            Valor absoluto do desconto progressivo.
        """
        if total > 1000:
            return total * 0.20
        if total > 500:
            return total * 0.10
        return 0.0

    def calculate_summary(self, reference_datetime: Optional[datetime] = None) -> CartSummary:
        """Retorna o resumo de totais com cupom e desconto progressivo.

        A ordem de cálculo é:
        1) Subtotal
        2) Cupom percentual
        3) Desconto progressivo por faixa

        Args:
            reference_datetime: Data/hora de referência para validação de expiração.

        Returns:
            Resumo contendo subtotal, descontos e total final.
        """
        current_datetime = reference_datetime or datetime.now()
        subtotal = self.calculate_total()

        coupon_discount = 0.0
        if self.coupon is not None:
            coupon_is_valid = self.coupon.is_active
            if self.coupon.expires_at is not None and current_datetime > self.coupon.expires_at:
                coupon_is_valid = False
            if subtotal < self.coupon.min_purchase:
                coupon_is_valid = False

            if coupon_is_valid:
                coupon_discount = subtotal * (self.coupon.discount_percent / 100)

        discounted_after_coupon = max(subtotal - coupon_discount, 0.0)
        progressive_discount = self._calculate_progressive_discount(discounted_after_coupon)
        total = max(discounted_after_coupon - progressive_discount, 0.0)

        return CartSummary(
            subtotal=subtotal,
            coupon_discount=coupon_discount,
            progressive_discount=progressive_discount,
            total=total,
        )

    def calculate_total_with_discount(self) -> float:
        """
        Calcula o valor total com descontos aplicados.

        A ordem aplicada é cupom percentual seguido de desconto progressivo:
        - 10% de desconto progressivo para compras acima de R$ 500.
        - 20% de desconto progressivo para compras acima de R$ 1000.

        Returns:
            float: O valor total com o desconto aplicado.
        """
        return self.calculate_summary().total
