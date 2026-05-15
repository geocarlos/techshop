from typing import Generator

from fastapi.testclient import TestClient
import pytest

from src.main import app, cart
from src.models import Product


@pytest.fixture(autouse=True)
def reset_cart_state() -> Generator[None, None, None]:
    """Reset global cart state before and after each API test."""
    # Arrange
    cart.items = []
    cart.remove_coupon()

    # Act
    yield

    # Assert
    cart.items = []
    cart.remove_coupon()


@pytest.fixture
def client() -> TestClient:
    """Provide a FastAPI TestClient instance."""
    # Arrange / Act / Assert
    return TestClient(app)


def test_read_root_returns_html_with_featured_products(client: TestClient) -> None:
    """Return home page HTML with featured products and navigation.

    Verifica se a página home é renderizada com Jinja2 contendo elementos esperados.
    """
    # Arrange

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "ExpressCommerce" in response.text
    assert "Produtos em destaque" in response.text
    assert "iPhone 13 128GB" in response.text


def test_get_cart_page_returns_html_with_summary(client: TestClient) -> None:
    """Return cart page HTML with cart summary.

    Verifica se a página do carrinho é renderizada com Jinja2 contendo
    o resumo e estrutura esperada.
    """
    # Arrange

    # Act
    response = client.get("/cart")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Carrinho" in response.text
    assert "Seu carrinho está vazio" in response.text


def test_get_cart_summary_returns_zeroed_totals_for_empty_cart(client: TestClient) -> None:
    """Return zeroed summary when the cart has no items."""
    # Arrange

    # Act
    response = client.get("/cart/summary")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "subtotal": 0.0,
        "coupon_discount": 0.0,
        "progressive_discount": 0.0,
        "total": 0.0,
    }


def test_apply_coupon_returns_not_found_for_unknown_code(client: TestClient) -> None:
    """Return 404 when trying to apply a non-existing coupon code."""
    # Arrange

    # Act
    response = client.post("/cart/apply-coupon", json={"code": "NOPE"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Coupon not found"}


def test_apply_coupon_returns_bad_request_when_subtotal_below_minimum(client: TestClient) -> None:
    """Return 400 when cart subtotal is below coupon minimum purchase."""
    # Arrange

    # Act
    response = client.post("/cart/apply-coupon", json={"code": "SAVE10"})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Cart subtotal is below coupon minimum purchase"}


def test_apply_coupon_returns_updated_summary_with_coupon_and_progressive(
    client: TestClient,
) -> None:
    """Apply coupon and return summary using coupon then progressive discount order."""
    # Arrange
    cart.add_item(Product(id=1, name="Notebook", price=200.0), 3)  # subtotal 600

    # Act
    response = client.post("/cart/apply-coupon", json={"code": "SAVE10"})

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["subtotal"] == pytest.approx(600.0)
    assert payload["coupon_discount"] == pytest.approx(60.0)
    assert payload["progressive_discount"] == pytest.approx(54.0)
    assert payload["total"] == pytest.approx(486.0)


def test_remove_coupon_returns_summary_without_coupon_discount(client: TestClient) -> None:
    """Remove previously applied coupon and keep only progressive discount."""
    # Arrange
    cart.add_item(Product(id=1, name="Notebook", price=200.0), 3)  # subtotal 600
    apply_response = client.post("/cart/apply-coupon", json={"code": "SAVE10"})
    assert apply_response.status_code == 200

    # Act
    response = client.delete("/cart/coupon")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "subtotal": 600.0,
        "coupon_discount": 0.0,
        "progressive_discount": 60.0,
        "total": 540.0,
    }


def test_add_to_cart_returns_updated_summary(client: TestClient) -> None:
    """Add item via API and return updated cart summary."""
    # Arrange

    # Act
    response = client.post("/cart/add", json={"product_id": 1, "quantity": 2})

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["subtotal"] == pytest.approx(4998.0)
    assert payload["coupon_discount"] == pytest.approx(0.0)
    assert payload["progressive_discount"] == pytest.approx(999.6)
    assert payload["total"] == pytest.approx(3998.4)


def test_remove_from_cart_returns_zeroed_summary_when_empty(client: TestClient) -> None:
    """Remove item via API and return zeroed summary for empty cart."""
    # Arrange
    add_response = client.post("/cart/add", json={"product_id": 1, "quantity": 1})
    assert add_response.status_code == 200

    # Act
    response = client.delete("/cart/remove/1")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "subtotal": 0.0,
        "coupon_discount": 0.0,
        "progressive_discount": 0.0,
        "total": 0.0,
    }


def test_add_to_cart_returns_404_for_unknown_product(client: TestClient) -> None:
    """Return 404 when adding a non-existing product to cart."""
    # Arrange

    # Act
    response = client.post("/cart/add", json={"product_id": 999, "quantity": 1})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_api_search_returns_filtered_products(client: TestClient) -> None:
    """Return product list filtered by query term."""
    # Arrange

    # Act
    response = client.get("/api/search", params={"q": "iphone"})

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert "iPhone" in payload[0]["name"]


def test_swagger_ui_is_available(client: TestClient) -> None:
    """Expose interactive Swagger UI for API documentation."""
    # Arrange

    # Act
    response = client.get("/docs")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "swagger-ui" in response.text.lower()
    assert "/openapi.json" in response.text


def test_openapi_schema_documents_api_routes_only(client: TestClient) -> None:
    """Document JSON API routes and omit server-rendered HTML routes."""
    # Arrange

    # Act
    response = client.get("/openapi.json")

    # Assert
    assert response.status_code == 200
    schema = response.json()
    paths = schema["paths"]

    assert schema["info"]["title"] == "TechShop API"
    assert "/api/status" in paths
    assert "/api/search" in paths
    assert "/cart/add" in paths
    assert "/cart/apply-coupon" in paths
    assert "/" not in paths
    assert "/cart" not in paths
    assert "/checkout" not in paths

    apply_coupon_operation = paths["/cart/apply-coupon"]["post"]
    request_content = apply_coupon_operation["requestBody"]["content"]
    assert apply_coupon_operation["tags"] == ["Cart"]
    assert "application/json" in request_content
    assert "application/x-www-form-urlencoded" in request_content


def test_search_page_returns_html(client: TestClient) -> None:
    """Render search page as HTML using home template with filters."""
    # Arrange

    # Act
    response = client.get("/search", params={"q": "macbook"})

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "MacBook" in response.text


def test_checkout_page_redirects_when_cart_is_empty(client: TestClient) -> None:
    """Redirect checkout access back to cart when there are no items."""
    # Arrange

    # Act
    response = client.get("/checkout", follow_redirects=False)

    # Assert
    assert response.status_code == 303
    assert response.headers["location"] == "/cart"


def test_checkout_page_returns_html_with_cart_summary(client: TestClient) -> None:
    """Render checkout page when the cart has items."""
    # Arrange
    cart.add_item(Product(id=1, name="Notebook", price=200.0), 2)

    # Act
    response = client.get("/checkout")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Finalizar pedido" in response.text
    assert "Resumo final" in response.text


def test_checkout_submission_returns_confirmation_and_clears_cart(client: TestClient) -> None:
    """Submit checkout form, render confirmation and clear the cart."""
    # Arrange
    cart.add_item(Product(id=1, name="Notebook", price=200.0), 2)

    # Act
    response = client.post(
        "/checkout",
        data={
            "full_name": "Geo Carlos",
            "email": "geo@example.com",
            "address": "Rua Central, 100 - Sao Paulo",
            "payment_method": "pix",
        },
    )

    # Assert
    assert response.status_code == 200
    assert "Compra concluída com sucesso" in response.text
    assert "Geo Carlos" in response.text
    assert cart.items == []
    assert cart.coupon is None


def test_checkout_submission_returns_bad_request_for_empty_cart(client: TestClient) -> None:
    """Reject checkout submission when cart is empty."""
    # Arrange

    # Act
    response = client.post(
        "/checkout",
        data={
            "full_name": "Geo Carlos",
            "email": "geo@example.com",
            "address": "Rua Central, 100 - Sao Paulo",
            "payment_method": "pix",
        },
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Cart is empty"}
