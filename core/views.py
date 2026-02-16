from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages


from django.db import transaction

from .models import Product, Cart, CartItem, Order, OrderItem


def home_view(request):
    return render(request, "home.html")


def about_view(request):
    return render(request, "about.html")


def contact_view(request):
    return render(request, "contact.html")


# def products_view(request):
#     return render(request, "products.html")


@login_required
def profile_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "profile.html")


# -----------------------------
# PRODUCT VIEWS
# -----------------------------


def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, "products/product_list.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "products/product_detail.html", {"product": product})


# -----------------------------
# CART VIEWS
# -----------------------------


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", product.min_order_quantity))

    # Check stock
    if product.stock_quantity < quantity:
        messages.error(
            request, f"Sorry, only {product.stock_quantity} left in stock.")
        return redirect("product_detail", slug=product.slug)

    # Check min/max limits
    if quantity < product.min_order_quantity:
        messages.error(
            request, f"Minimum order quantity for this item is {product.min_order_quantity}."
        )
        return redirect("product_detail", slug=product.slug)

    if product.max_order_quantity and quantity > product.max_order_quantity:
        messages.error(
            request, f"Maximum order quantity for this item is {product.max_order_quantity}."
        )
        return redirect("product_detail", slug=product.slug)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product)

    if not created:
        new_quantity = cart_item.quantity + quantity
        # Final stock check for combined quantity
        if product.stock_quantity < new_quantity:
            messages.error(
                request,
                f"Cannot add more. You already have {cart_item.quantity} in cart and total stock is {product.stock_quantity}.",
            )
            return redirect("cart")
        cart_item.quantity = new_quantity

    else:
        cart_item.quantity = quantity

    cart_item.save()
    messages.success(request, f"Added {product.name} to cart")
    return redirect("cart")


@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.items.all() if cart else []

    total = sum(item.get_total_price() for item in items)

    return render(
        request,
        "cart/cart.html",
        {
            "cart": cart,
            "items": items,
            "total": total,
        },
    )


@login_required
def update_cart_item(request, item_id):
    """Update the quantity of a cart item"""
    if request.method == "POST":
        cart_item = get_object_or_404(
            CartItem, id=item_id, cart__user=request.user)
        product = cart_item.product
        quantity = int(request.POST.get("quantity", 1))

        success = False
        message = ""

        if quantity > 0:
            # Check limits
            if quantity < product.min_order_quantity:
                message = f"Minimum order quantity for {product.name} is {product.min_order_quantity}."
            elif product.max_order_quantity and quantity > product.max_order_quantity:
                message = f"Maximum order quantity for {product.name} is {product.max_order_quantity}."
            # Check stock
            elif product.stock_quantity < quantity:
                message = f"Not enough stock for {product.name}. Only {product.stock_quantity} available."
            else:
                cart_item.quantity = quantity
                cart_item.save()
                success = True
                message = "Cart updated successfully"
        else:
            cart_item.delete()
            success = True
            message = "Item removed from cart"

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            from django.http import JsonResponse

            cart = cart_item.cart
            items = cart.items.all()
            total = sum(item.get_total_price() for item in items)

            return JsonResponse(
                {
                    "success": success,
                    "message": message,
                    "item_id": item_id,
                    "quantity": cart_item.quantity if quantity > 0 else 0,
                    "item_total": float(cart_item.get_total_price()) if quantity > 0 else 0,
                    "cart_total": float(total),
                    "cart_count": items.count(),
                }
            )

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

    return redirect("cart")


@login_required
def remove_cart_item(request, item_id):
    """Remove an item from the cart"""
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"{product_name} removed from cart")
    return redirect("cart")


# -----------------------------
# CHECKOUT & ORDER (COD)
# -----------------------------


@login_required
@transaction.atomic
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty")
        return redirect("product_list")

    if request.method == "POST":
        # Final stock check before processing
        for item in cart.items.all():
            if item.product.stock_quantity < item.quantity:
                messages.error(
                    request,
                    f"Sorry, {item.product.name} just went out of stock or has insufficient quantity. Please adjust your cart.",
                )
                return redirect("cart")

        # Create order
        order = Order.objects.create(
            user=request.user,
            payment_method="COD",
            status="PLACED",
        )

        # Move cart items → order items & Deduct Stock
        for item in cart.items.all():
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            # Deduct stock
            product = item.product
            product.stock_quantity -= item.quantity
            product.save()

        # Clear cart
        cart.items.all().delete()

        messages.success(
            request, "Order placed successfully (Cash on Delivery)")
        return redirect("order_success")

    total = sum(item.get_total_price() for item in cart.items.all())

    return render(
        request,
        "checkout/checkout.html",
        {
            "cart": cart,
            "total": total,
        },
    )


@login_required
def order_success(request):
    return render(request, "checkout/order_success.html")
