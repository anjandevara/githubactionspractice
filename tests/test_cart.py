from cart import add_item, total, apply_discount


def test_add_item_adds_one_row():
    cart = add_item([], "apple", 0.50)
    assert cart == [{"name": "apple", "price": 0.50, "quantity": 1}]


def test_total_multiplies_price_by_quantity():
    cart = add_item(add_item([], "apple", 0.50, 2), "bread", 1.20)
    assert total(cart) == 2.20


def test_apply_discount_takes_percent_off():
    assert apply_discount(100.0, 10) == 90.0
