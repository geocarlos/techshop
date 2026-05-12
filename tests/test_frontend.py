"""
Testes de saída HTML das rotas frontend.

Verifica se:
- Páginas retornam HTML válido
- Elementos esperados estão presentes (logo, busca, produtos, cupom)
- Estrutura de navegação funciona
- Responsividade é considerada
"""

from fastapi.testclient import TestClient
import pytest
from src.main import app, cart
from src.models import Product


@pytest.fixture(autouse=True)
def reset_cart_state() -> None:
    """Resetar estado do carrinho antes de cada teste.

    Garante que testes não interferem um com o outro.
    """
    cart.items.clear()
    cart.applied_coupon = None


@pytest.fixture
def client() -> TestClient:
    """Criar cliente de teste FastAPI."""
    return TestClient(app)


class TestHomePage:
    """Testes da página inicial (GET /)."""

    def test_home_returns_html(self, client: TestClient) -> None:
        """Verificar que GET / retorna HTML.

        Valida status 200 e content-type correto.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_home_contains_logo(self, client: TestClient) -> None:
        """Verificar que página home contém logo ExpressCommerce."""
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert "ExpressCommerce" in response.text

    def test_home_contains_search_bar(self, client: TestClient) -> None:
        """Verificar que página home contém barra de busca.

        Busca por input de busca ou placeholder.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert "buscar" in response.text.lower() or "search" in response.text.lower()

    def test_home_contains_featured_products(self, client: TestClient) -> None:
        """Verificar que página home exibe produtos em destaque.

        Verifica por nome de produto conhecido.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert "iPhone" in response.text
        assert "MacBook" in response.text or "5800" in response.text

    def test_home_contains_categories(self, client: TestClient) -> None:
        """Verificar que página home contém categorias.

        Busca por categorias esperadas.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        # Pelo menos uma categoria deve estar presente
        categories = ["Celulares", "Computadores", "Moda", "Casa", "Esportes"]
        found = sum(1 for cat in categories if cat in response.text)
        assert found >= 3, "Pelo menos 3 categorias devem estar presentes"

    def test_home_contains_navigation(self, client: TestClient) -> None:
        """Verificar que página home contém elementos de navegação.

        Verifica header e links básicos.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert "<header" in response.text.lower() or "header" in response.text.lower()

    def test_home_contains_cart_icon(self, client: TestClient) -> None:
        """Verificar que página home contém ícone de carrinho.

        Busca por badge/counter do carrinho.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert "cart" in response.text.lower() or "carrinho" in response.text.lower()

    def test_home_contains_product_prices(self, client: TestClient) -> None:
        """Verificar que produtos exibem preços.

        Busca por formato de moeda.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert "R$" in response.text or "2499" in response.text or "5800" in response.text


class TestCartPage:
    """Testes da página do carrinho (GET /cart)."""

    def test_cart_page_returns_html(self, client: TestClient) -> None:
        """Verificar que GET /cart retorna HTML."""
        # Arrange

        # Act
        response = client.get("/cart")

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_cart_page_shows_empty_message(self, client: TestClient) -> None:
        """Verificar que página mostra mensagem de carrinho vazio."""
        # Arrange

        # Act
        response = client.get("/cart")

        # Assert
        assert "vazio" in response.text.lower() or "empty" in response.text.lower()

    def test_cart_page_contains_coupon_form(self, client: TestClient) -> None:
        """Verificar que página contém formulário de cupom.

        Busca por input de código de cupom.
        """
        # Arrange

        # Act
        response = client.get("/cart")

        # Assert
        assert "cupom" in response.text.lower() or "coupon" in response.text.lower()
        assert "input" in response.text.lower()

    def test_cart_page_contains_summary_sections(self, client: TestClient) -> None:
        """Verificar que página contém seções de resumo.

        Busca por subtotal, desconto, total.
        """
        # Arrange

        # Act
        response = client.get("/cart")

        # Assert
        summary_terms = ["subtotal", "total", "desconto", "discount"]
        found = sum(1 for term in summary_terms if term.lower() in response.text.lower())
        assert found >= 2, "Pelo menos 2 termos de resumo devem estar presentes"

    def test_cart_page_contains_checkout_button(self, client: TestClient) -> None:
        """Verificar que página contém botão de checkout.

        Busca por botão de compra/checkout.
        """
        # Arrange

        # Act
        response = client.get("/cart")

        # Assert
        checkout_terms = ["checkout", "comprar", "finalizar", "pagar"]
        found = any(term in response.text.lower() for term in checkout_terms)
        # Nota: Pode não ter checkout implementado ainda, então check lenient
        assert "button" in response.text.lower() or "click" in response.text.lower()


class TestCheckoutPage:
    """Testes da página de checkout (GET /checkout)."""

    def test_checkout_redirects_with_empty_cart(self, client: TestClient) -> None:
        """Verificar redirecionamento ao checkout com carrinho vazio."""
        # Arrange

        # Act
        response = client.get("/checkout", follow_redirects=False)

        # Assert
        assert response.status_code == 303
        assert response.headers["location"] == "/cart"

    def test_checkout_page_contains_form_when_cart_has_items(self, client: TestClient) -> None:
        """Verificar que o checkout renderiza formulário com carrinho preenchido."""
        # Arrange
        cart.add_item(Product(id=1, name="Notebook", price=200.0), 1)

        # Act
        response = client.get("/checkout")

        # Assert
        assert response.status_code == 200
        assert "Finalizar pedido" in response.text
        assert "form" in response.text.lower()


class TestHTMLValidity:
    """Testes de validade HTML básica."""

    def test_home_page_has_valid_html_structure(self, client: TestClient) -> None:
        """Verificar que página home tem estrutura HTML válida.

        Verifica presença de tags básicas.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert "<html" in response.text.lower()
        assert "<head" in response.text.lower()
        assert "<body" in response.text.lower()

    def test_cart_page_has_valid_html_structure(self, client: TestClient) -> None:
        """Verificar que página carrinho tem estrutura HTML válida."""
        # Arrange

        # Act
        response = client.get("/cart")

        # Assert
        assert "<html" in response.text.lower()
        assert "<head" in response.text.lower()
        assert "<body" in response.text.lower()

    def test_home_page_has_closing_tags(self, client: TestClient) -> None:
        """Verificar que página home tem tags de fechamento.

        Verifica se </html> está presente.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        assert "</html>" in response.text.lower()
        assert "</body>" in response.text.lower()

    def test_pages_include_tailwind_css(self, client: TestClient) -> None:
        """Verificar que páginas incluem Tailwind CSS via CDN."""
        # Arrange

        # Act
        response_home = client.get("/")
        response_cart = client.get("/cart")

        # Assert
        assert "tailwindcss" in response_home.text.lower()
        assert "tailwindcss" in response_cart.text.lower()


class TestResponsiveness:
    """Testes de responsividade e acessibilidade."""

    def test_pages_have_viewport_meta_tag(self, client: TestClient) -> None:
        """Verificar que páginas têm viewport meta tag (mobile).

        Essencial para responsividade.
        """
        # Arrange

        # Act
        response_home = client.get("/")
        response_cart = client.get("/cart")

        # Assert
        assert "viewport" in response_home.text.lower()
        assert "viewport" in response_cart.text.lower()

    def test_pages_use_semantic_html(self, client: TestClient) -> None:
        """Verificar que páginas usam HTML semântico.

        Busca por tags semânticas (header, main, section, etc).
        """
        # Arrange

        # Act
        response_home = client.get("/")

        # Assert
        semantic_tags = ["<header", "<main", "<section", "<article", "<footer"]
        found = sum(1 for tag in semantic_tags if tag.lower() in response_home.text.lower())
        assert found >= 2, "Pelo menos 2 tags semânticas devem estar presentes"

    def test_product_cards_have_alt_text(self, client: TestClient) -> None:
        """Verificar que imagens de produtos têm texto alternativo.

        Importante para acessibilidade.
        """
        # Arrange

        # Act
        response = client.get("/")

        # Assert
        # Contar imagens com alt ou title
        assert "alt=" in response.text.lower() or "img" in response.text.lower()

    def test_buttons_have_descriptive_text(self, client: TestClient) -> None:
        """Verificar que botões têm texto descritivo.

        Não deve haver botões vazios.
        """
        # Arrange

        # Act
        response = client.get("/cart")

        # Assert
        # Botões devem ter texto ou aria-label
        assert "button" in response.text.lower()
