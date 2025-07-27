from django.shortcuts import render, get_object_or_404,redirect
from .cart import Cart
from django.views.decorators.http import require_POST
from .forms import *  # <-- import your form
from django.contrib.auth import login
from app.models import *
# Create your views here.
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.core.paginator import Paginator

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def store(request):
    products = Product.objects.all()

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
    # 🔍 Search
    search_query = request.GET.get("search", "")
    if search_query:
        products = products.filter(name__icontains=search_query)

    # 🎨 Color Filter
    color = request.GET.get("color", "")
    if color:
        products = products.filter(color__iexact=color)

    # 📏 Size Filter
    size = request.GET.get("size", "")
    if size:
        products = products.filter(size__iexact=size)

    # 🟡 Category Filter
    category = request.GET.get("category", "")
    if category:
        products = products.filter(category__iexact=category)

    # 💰 Price Filter
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # 📦 Distinct filters for form
    categories = Product.objects.values_list('category', flat=True).distinct()
    sizes = Product.objects.values_list('size', flat=True).distinct()
    colors = Product.objects.values_list('color', flat=True).distinct()

    # 🔢 Pagination
    paginator = Paginator(products, 8)  # 8 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
        'selected': {
            'search': search_query,
            'color': color,
            'size': size,
            'category': category,
            'price_min': price_min or "",
            'price_max': price_max or ""
        },
     'favorite_ids': favorite_ids

    }

    return render(request, "store/store.html", context)



def Home(request):
    products= Product.objects.all()

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    context = {
        "products":products,
                'favorite_ids': favorite_ids,

    }
    return render(request,'store/Home.html',context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=pk)[:4]  # Show 4 related products


    return render(request, 'store/product_detail.html', {'product': product, 'related_products': related_products,                'favorite_ids': favorite_ids,
})



def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    cart.add(product)
    return redirect('view_cart')



def view_cart(request):

    cart = Cart(request)
    cart_items = dict(cart.get_items())
    total = cart.get_total_price()

    return render(request, 'store/cart.html', {
        'cart_items': cart_items.items(),
        'total': total,
    })


def remove_from_cart(request, pk):
    cart = Cart(request)
    cart.remove(pk)
    return redirect('view_cart')


@require_POST
def update_cart(request, pk):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(pk, quantity)
    return redirect('view_cart')




def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after register
            return redirect('home')  # or redirect to 'view_cart', etc.
    else:
        form = CustomRegisterForm()
    return render(request, 'auth/register.html', {'form': form})

from django.contrib import messages


def checkout_info(request):
    if request.method == 'POST':
        # Save all form fields to session
        request.session['checkout_info'] = {
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'zip_code': request.POST.get('zip_code'),
        }
        return redirect('stripe_checkout')
    return render(request, 'store/checkout_info.html')


@login_required
def create_checkout_session(request):
    cart = Cart(request)
    items = dict(cart.get_items())
    checkout_info = request.session.get('checkout_info', {})
    order = Order.objects.create(
        user=request.user,
        email=checkout_info.get('email', ''),
        phone=checkout_info.get('phone', ''),
        address=checkout_info.get('address', ''),
        zip_code=checkout_info.get('zip_code', ''),
        payment_staus='pending',
    )
    for product_id, item in items.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=item['price']
        )

    line_items = [
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': int(float(item['price']) * 100),
            },
            'quantity': item['quantity'],
        }
        for item in items.values()
    ]

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(f'/checkout/success/{order.id}/'),
        cancel_url=request.build_absolute_uri("/checkout/cancel/"),
    )

    # 5. Save Payment Intent or Session ID to Order
    order.stripe_payment_intent = session.payment_intent or session.id
    order.save()

    return redirect(session.url, code=303)

@login_required
def checkout_success(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.payment_staus = 'paid'
        order.status = 'pending'
        order.save()
        Cart(request).clear()
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
    return render(request, 'store/checkout_success.html')

@require_POST
@login_required
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.status = 'cancelled'
        order.save()
        messages.success(request, "Order cancelled and payment refunded.")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    return redirect('orders')



@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'cancelled':
        order.delete()
        messages.success(request, "Order deleted successfully.")
    else:
        messages.error(request, "Only cancelled orders can be deleted.")

    return redirect('orders')


def checkout_cancel(request):
    return render(request, 'store/checkout_cancel.html')


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user,payment_staus="paid").prefetch_related('orderitem_set__product')
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status == 'pending':
            form = OrderAddressForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect('orders')
    else:
        for order in orders:
            if order.status == 'pending':
                order.address_form = OrderAddressForm(instance=order)


    return render(request, 'store/my_orders.html', {'orders': orders})




@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    return redirect('favorites')

@login_required
def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.filter(user=request.user, product=product).delete()
    return redirect('favorites')

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/favorites.html', {'favorites': favorites})


def about(request):
    return render(request, 'store/about.html')



from django.contrib import messages

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            NewsletterEmail.objects.get_or_create(email=email)
            messages.success(request, "Thanks for subscribing!")
    return redirect('home')



@login_required
def return_requests_list(request):
    requests = ReturnRequest.objects.filter(user=request.user)
    return render(request, 'returns/return_requests_list.html', {'requests': requests})

from django.utils.timezone import now


@login_required
def create_return_request(request):
    # ✅ Filter only delivered OrderItems
    delivered_items = OrderItem.objects.filter(
        order__user=request.user,
        order__status='delivered'
    )

    if request.method == 'POST':
        order_item_id = request.POST.get('order_item')
        reason = request.POST.get('reason')
        pickup_date = now().date()

        order_item = OrderItem.objects.get(id=order_item_id, order__user=request.user)

        ReturnRequest.objects.create(
            user=request.user,
            order_item=order_item,
            reason=reason,
            pickup_date=pickup_date
        )
        messages.success(request, 'Your return request has been submitted.')
        return redirect('return_requests')

    return render(request, 'returns/create_return_request.html', {
        'delivered_items': delivered_items
    })


