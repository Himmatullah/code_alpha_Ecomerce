
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category


def home(request):
    products = Product.objects.filter(
        is_active=True
    ).select_related('category').order_by('-created_at')

    categories = Category.objects.all().order_by('name')

    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    selected_category = None

    if category_id.isdigit():
        selected_category = Category.objects.filter(
            pk=int(category_id)
        ).first()

        if selected_category:
            products = products.filter(category=selected_category)

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    }

    return render(request, 'products/home.html', context)


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category'),
        pk=pk,
        is_active=True
    )

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk).order_by('-created_at')[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }

    return render(request, 'products/product_detail.html', context)
