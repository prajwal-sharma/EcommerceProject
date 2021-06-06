from django.shortcuts import render
from store.models import Product, Variation
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Create your views here.
def store(request, category_slug=None):
    if category_slug is not None:
        products = Product.objects.all().filter(category__slug=category_slug, is_available=True).order_by('id')
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = len(products)

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = len(products)
    context = {
        "products": paged_products,
        "product_count": product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    product = Product.objects.get(slug=str(product_slug))

    try:
        product_presence = product.product.get(cart__cart_id__isnull=False)
    except:
        product_presence = None
    context = {
        "product": product,
        'product_presence': product_presence,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    products = None
    if 'keyword' in request.GET:
        keyword = str(request.GET.get('keyword'))
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__contains=keyword) | Q(product_name__icontains=keyword))

    product_count = len(products)
    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)
