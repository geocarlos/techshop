import pytest

from src.cart import ShoppingCart
from src.models import Product


def make_product(product_id: int, price: float, name: str = "Produto") -> Product:
    """Create a product instance for test scenarios.

    Args:
        product_id: Unique product identifier.
        price: Product unit price.
        name: Product name.

    Returns:
        A validated Product instance.
    """
    return Product(id=product_id, name=name, price=price)


def test_calculate_total_without_discount_below_threshold() -> None:
    """Ensure totals below the first threshold keep original value."""
    # Arrange
    cart = ShoppingCart()
    cart.add_item(make_product(1, 100.0), 3)  # total 300

    # Act
    total = cart.calculate_total()
    discounted_total = cart.calculate_total_with_discount()

    # Assert
    assert total == pytest.approx(300.0)
    assert discounted_total == pytest.approx(300.0)


def test_calculate_total_with_10_percent_discount_above_500() -> None:
    """Apply 10% discount when total is strictly greater than 500."""
    # Arrange
    cart = ShoppingCart()
    cart.add_item(make_product(1, 120.0), 5)  # total 600

    # Act
    total = cart.calculate_total()
    discounted_total = cart.calculate_total_with_discount()

    # Assert
    assert total == pytest.approx(600.0)
    assert discounted_total == pytest.approx(540.0)


def test_calculate_total_with_20_percent_discount_above_1000() -> None:
    """Apply 20% discount when total is strictly greater than 1000."""
    # Arrange
    cart = ShoppingCart()
    cart.add_item(make_product(1, 250.0), 5)  # total 1250

    # Act
    total = cart.calculate_total()
    discounted_total = cart.calculate_total_with_discount()

    # Assert
    assert total == pytest.approx(1250.0)
    assert discounted_total == pytest.approx(1000.0)


def test_discount_thresholds_are_strictly_greater_than_limits() -> None:
    """Verify edge totals 500 and 1000 do not trigger the higher tier."""
    # Arrange
    cart_500 = ShoppingCart()
    cart_500.add_item(make_product(1, 100.0), 5)  # total 500

    cart_1000 = ShoppingCart()
    cart_1000.add_item(make_product(1, 100.0), 10)  # total 1000

    # Act
    total_500_with_discount = cart_500.calculate_total_with_discount()
    total_1000_with_discount = cart_1000.calculate_total_with_discount()

    # Assert
    assert total_500_with_discount == pytest.approx(500.0)
    assert total_1000_with_discount == pytest.approx(900.0)


def test_add_item_with_same_product_aggregates_quantity() -> None:
    """Aggregate quantities when adding the same product multiple times."""
    # Arrange
    cart = ShoppingCart()
    product = make_product(1, 150.0)

    cart.add_item(product, 2)
    cart.add_item(product, 2)

    # Act
    items_count = len(cart.items)
    aggregated_quantity = cart.items[0].quantity
    discounted_total = cart.calculate_total_with_discount()

    # Assert
    assert items_count == 1
    assert aggregated_quantity == 4
    assert discounted_total == pytest.approx(540.0)  # 600 - 10%


def test_remove_item_removes_product_from_cart() -> None:
    """Remove a product from the cart by its identifier."""
    # Arrange
    cart = ShoppingCart()
    cart.add_item(make_product(1, 100.0), 1)
    cart.add_item(make_product(2, 200.0), 1)

    # Act
    cart.remove_item(1)
    items_count = len(cart.items)
    remaining_product_id = cart.items[0].product.id

    # Assert
    assert items_count == 1
    assert remaining_product_id == 2
