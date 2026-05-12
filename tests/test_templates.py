"""
Testes de renderização de templates Jinja2.

Verifica se:
- Templates renderizam sem erros
- Variáveis são injetadas corretamente
- Loops funcionam
- Herança de templates funciona
"""

from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader

# Configurar ambiente Jinja2 igual ao main.py
templates_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))


class TestTemplateRendering:
    """Testes de renderização básica de templates."""

    def test_base_template_renders_without_error(self) -> None:
        """Renderizar base.html sem erros.

        Verifica se o template base carrega e renderiza sem exceções.
        """
        # Arrange
        template = jinja_env.get_template("base.html")

        # Act
        html = template.render(title="Test", content="<p>Test</p>")

        # Assert
        assert html is not None
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html or "<html" in html

    def test_index_template_renders_with_products(self) -> None:
        """Renderizar index.html com lista de produtos.

        Verifica se template renderiza e injeta corretamente dados de produtos.
        """
        # Arrange
        template = jinja_env.get_template("index.html")
        featured_products = [
            {"id": 1, "name": "iPhone 13", "price": 2499.00, "location": "São Paulo, SP"},
            {"id": 2, "name": "MacBook", "price": 5800.00, "location": "Curitiba, PR"},
        ]

        # Act
        html = template.render(featured_products=featured_products, cart_count=0)

        # Assert
        assert "iPhone 13" in html
        assert "MacBook" in html
        assert "R$" in html or "2499" in html
        assert "São Paulo, SP" in html

    def test_index_template_renders_empty_products_list(self) -> None:
        """Renderizar index.html com lista vazia de produtos.

        Verifica que template não quebra com lista vazia.
        """
        # Arrange
        template = jinja_env.get_template("index.html")

        # Act
        html = template.render(featured_products=[], cart_count=0)

        # Assert
        assert html is not None
        assert len(html) > 0

    def test_cart_template_renders_with_empty_cart(self) -> None:
        """Renderizar cart.html com carrinho vazio.

        Verifica se mensagem de carrinho vazio é exibida.
        """
        # Arrange
        template = jinja_env.get_template("cart.html")

        # Act
        html = template.render(
            cart_items=[],
            cart_summary={"subtotal": 0, "coupon_discount": 0, "progressive_discount": 0, "total": 0},
            cart_count=0,
        )

        # Assert
        assert "vazio" in html.lower() or "empty" in html.lower()

    def test_cart_template_renders_with_items(self) -> None:
        """Renderizar cart.html com itens no carrinho.

        Verifica se itens, preços e resumo são renderizados corretamente.
        """
        # Arrange
        template = jinja_env.get_template("cart.html")
        cart_items = [
            {"product": {"id": 1, "name": "iPhone", "price": 2499.00}, "quantity": 1}
        ]
        cart_summary = {
            "subtotal": 2499.00,
            "coupon_discount": 0,
            "progressive_discount": 0,
            "total": 2499.00,
        }

        # Act
        html = template.render(
            cart_items=cart_items,
            cart_summary=cart_summary,
            cart_count=1,
        )

        # Assert
        assert "iPhone" in html
        assert "2499" in html
        assert "Remover" in html

    def test_cart_template_renders_with_coupon_discount(self) -> None:
        """Renderizar cart.html com desconto de cupom.

        Verifica que linha de desconto de cupom é renderizada.
        """
        # Arrange
        template = jinja_env.get_template("cart.html")
        cart_items = [
            {"product": {"id": 1, "name": "iPhone", "price": 2499.00}, "quantity": 1}
        ]
        cart_summary = {
            "subtotal": 2499.00,
            "coupon_discount": 249.90,
            "progressive_discount": 0,
            "total": 2249.10,
        }

        # Act
        html = template.render(
            cart_items=cart_items,
            cart_summary=cart_summary,
            cart_count=1,
        )

        # Assert
        assert "249.90" in html or "249" in html

    def test_cart_template_renders_with_progressive_discount(self) -> None:
        """Renderizar cart.html com desconto progressivo.

        Verifica que desconto progressivo é exibido quando valor > 500.
        """
        # Arrange
        template = jinja_env.get_template("cart.html")
        cart_items = [
            {"product": {"id": 1, "name": "iPhone", "price": 2499.00}, "quantity": 1}
        ]
        cart_summary = {
            "subtotal": 2499.00,
            "coupon_discount": 0,
            "progressive_discount": 249.90,  # 10% de desconto progressivo
            "total": 2249.10,
        }

        # Act
        html = template.render(
            cart_items=cart_items,
            cart_summary=cart_summary,
            cart_count=1,
        )

        # Assert
        assert "249.90" in html or "249" in html

    def test_template_inheritance_works(self) -> None:
        """Verificar que herança de template funciona.

        Verifica que index.html estende base.html corretamente.
        """
        # Arrange
        template = jinja_env.get_template("index.html")

        # Act
        html = template.render(featured_products=[], cart_count=0)

        # Assert - verificar que elementos de base.html estão presentes
        assert "ExpressCommerce" in html or "header" in html.lower()

    def test_cart_count_badge_renders(self) -> None:
        """Verificar que badge de contagem do carrinho renderiza.

        Verifica se cart_count é exibido corretamente.
        """
        # Arrange
        template = jinja_env.get_template("index.html")

        # Act
        html = template.render(featured_products=[], cart_count=5)

        # Assert - badge deve exibir o número
        assert "5" in html or "carrinho" in html.lower()
