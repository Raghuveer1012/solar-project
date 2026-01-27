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

    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    messages.success(request, "Product added to cart")
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
        # Create order
        order = Order.objects.create(
            user=request.user,
            payment_method="COD",
            status="PLACED",
        )

        # Move cart items → order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, "Order placed successfully (Cash on Delivery)")
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
