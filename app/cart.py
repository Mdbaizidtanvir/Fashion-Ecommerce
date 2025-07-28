class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]["quantity"] += quantity
        else:
            self.cart[product_id] = {
                "name": product.name,
                "price": str(product.price),
                "image": product.main_image.url if product.main_image else "",
                "quantity": quantity,
            }
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session["cart"] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def get_items(self):
        return self.cart.items()

    def get_total_price(self):
        return sum(float(item["price"]) * item["quantity"] for item in self.cart.values())

    
    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]["quantity"] = quantity
            else:
                del self.cart[product_id]  # Remove if quantity is 0
            self.save()

