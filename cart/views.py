
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from products.models import Product
from .models import Cart, CartItem


def get_user_cart(request, create=False):
    """
    Retrieve the cart belonging to the current user
    or the current anonymous session.
    """

    if request.user.is_authenticated:
        carts = Cart.objects.filter(
            user=request.user
        ).order_by('id')

        cart = carts.first()

        if cart is None and create:
            cart = Cart.objects.create(
                user=request.user
            )

        return cart

    # Anonymous customer
    session_key = request.session.session_key

    if not session_key and create:
        request.session['cart_initialized'] = True
        request.session.save()
        session_key = request.session.session_key

    if not session_key:
        return None

    carts = Cart.objects.filter(
        user__isnull=True,
        session_key=session_key
    ).order_by('id')

    cart = carts.first()

    if cart is None and create:
        cart = Cart.objects.create(
            session_key=session_key
        )

    return cart


def cart_detail(request):
    cart = get_user_cart(request)

    cart_items = []
    total = Decimal('0.00')
    total_quantity = 0

    if cart:
        cart_items = list(
            cart.items.select_related('product')
            .order_by('id')
        )

        for item in cart_items:
            total += item.subtotal
            total_quantity += item.quantity

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'total_quantity': total_quantity,
    }

    return render(request, 'cart/cart_detail.html', context)


@require_POST
def add_to_cart(request, product_id):

    quantity_text = request.POST.get('quantity', '1')

    try:
        quantity = int(quantity_text)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid quantity.')
        return redirect('home')

    if quantity < 1:
        messages.error(request, 'Quantity must be at least 1.')
        return redirect('home')

    with transaction.atomic():

        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=product_id,
            is_active=True
        )

        if product.stock < quantity:
            messages.error(
                request,
                'Not enough stock available.'
            )
            return redirect('product_detail', pk=product.id)

        cart = get_user_cart(request, create=True)

        item = (
            CartItem.objects.select_for_update()
            .filter(cart=cart, product=product)
            .first()
        )

        existing_quantity = item.quantity if item else 0
        new_quantity = existing_quantity + quantity

        if new_quantity > product.stock:
            messages.error(
                request,
                f'Only {product.stock} units are available.'
            )
            return redirect('product_detail', pk=product.id)

        if item:
            item.quantity = new_quantity
            item.save(update_fields=['quantity'])
        else:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )

    messages.success(
        request,
        f'{product.name} added to your cart.'
    )

    return redirect('cart_detail')


@require_POST
def update_cart(request, item_id):

    quantity_text = request.POST.get('quantity')

    try:
        quantity = int(quantity_text)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid quantity.')
        return redirect('cart_detail')

    if quantity < 1:
        messages.error(
            request,
            'Quantity must be at least 1.'
        )
        return redirect('cart_detail')

    cart = get_user_cart(request)

    if not cart:
        messages.error(request, 'Cart not found.')
        return redirect('cart_detail')

    with transaction.atomic():

        item = get_object_or_404(
            CartItem.objects.select_related('product'),
            id=item_id,
            cart=cart
        )

        product = get_object_or_404(
            Product.objects.select_for_update(),
            pk=item.product_id
        )

        # Re-read the item under a row lock.
        item = get_object_or_404(
            CartItem.objects.select_for_update(),
            pk=item.pk,
            cart=cart
        )

        if not product.is_active:
            messages.error(
                request,
                'This product is no longer available.'
            )
            return redirect('cart_detail')

        if quantity > product.stock:
            messages.error(
                request,
                f'Only {product.stock} units are available.'
            )
            return redirect('cart_detail')

        item.quantity = quantity
        item.save(update_fields=['quantity'])

    messages.success(request, 'Cart updated successfully.')

    return redirect('cart_detail')


@require_POST
def remove_from_cart(request, item_id):

    cart = get_user_cart(request)

    if not cart:
        messages.error(request, 'Cart not found.')
        return redirect('cart_detail')

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    item.delete()

    messages.success(
        request,
        'Product removed from your cart.'
    )

    return redirect('cart_detail')
