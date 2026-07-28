def add_item(cart, name, price, quantity=1):
    return cart + [{"name": name, "price": price, "quantity": quantity}]


def total(cart):
    return sum(item["price"] * item["quantity"] for item in cart)


def apply_discount(amount, percent):
    return round(amount * (1 - percent / 100), 2)
