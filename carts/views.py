from django.shortcuts import render, redirect, HttpResponse
from store.models import Product, Variation
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()

    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)  # get the object

    if current_user.is_authenticated:
        print("I AM LOGGED IN")
        try:
            cart = Cart.objects.filter(cart__user=current_user)
            if cart[0] is None:
                pass
        except IndexError:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            print("asfdsfasfasdfasdfasd")
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(key)
                # print(key, ":", value)
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        flag = 0
        if cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, user=current_user)
            for cart_item in cart_items:
                product_variation.sort(key=lambda x: x.variation_category)
                # print(product_variation == list(cart_item.variations.all().order_by('variation_category')))
                # print(product_variation)
                # print(list(cart_item.variations.all().order_by('variation_category')))
                if product_variation == list(cart_item.variations.all().order_by('variation_category')):
                    if len(product_variation) > 0:
                        cart_item.quantity += 1
                        cart_item.save()
                        flag = 1
                        break

            if flag == 0:
                print("yes 1 logged")
                cart_item = CartItem.objects.create(
                    product=product,
                    user=current_user,
                    cart=cart[0],
                    quantity=1,
                )
                # cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
                cart_item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                user=current_user,
                cart=cart,
                quantity=1,
            )
            print("yes 2 logged")
            if len(product_variation) > 0:
                for item in product_variation:
                    cart_item.variations.add(item)
            # print(cart_item.quantity)
            cart_item.save()
        return redirect('cart')
    else:
        print("IM A lOGGED OUT")
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(key)
                print(key, ":", value)
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()
        cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        flag = 0
        if cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, cart=cart)
            for cart_item in cart_items:
                product_variation.sort(key=lambda x: x.variation_category)
                # print(product_variation == list(cart_item.variations.all().order_by('variation_category')))
                # print(product_variation)
                # print(list(cart_item.variations.all().order_by('variation_category')))
                if product_variation == list(cart_item.variations.all().order_by('variation_category')):
                    if len(product_variation) > 0:
                        cart_item.quantity += 1
                        cart_item.save()
                        flag = 1
                        break

            if flag == 0:
                print("yes 1")
                cart_item = CartItem.objects.create(
                    product=product,
                    cart=cart,
                    quantity=1,
                )
                # cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
                cart_item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1,
            )
            print("yes 2")
            if len(product_variation) > 0:
                for item in product_variation:
                    cart_item.variations.add(item)
            # print(cart_item.quantity)
            cart_item.save()
        return redirect('cart')


def remove_a_product(request, product_id, cart_item_id):
    current_user = request.user
    if current_user.is_authenticated:
        cart_item = CartItem.objects.get(product__id=product_id, user=current_user, id=cart_item_id)
    else:
        cart_item = CartItem.objects.get(product=Product.objects.get(id=product_id),
                                         cart=Cart.objects.get(cart_id=_cart_id(request)), id=cart_item_id)
    cart_item.quantity -= 1
    if cart_item.quantity == 0:
        cart_item.delete()
        return redirect('cart')
    # print(cart_item.quantity)
    cart_item.save()
    return redirect('cart')


def remove_product(request, product_id, cart_item_id):
    current_user = request.user
    if current_user.is_authenticated:
        cart_item = CartItem.objects.get(product__id=product_id, user=current_user, id=cart_item_id)
    else:
        cart_item = CartItem.objects.get(product=Product.objects.get(id=product_id),
                                         cart=Cart.objects.get(cart_id=_cart_id(request)), id=cart_item_id)

    cart_item.delete()
    return redirect('cart')


def cart(request):
    total = quantity = 0
    # cart = Cart.objects.get(cart_id=_cart_id(request))
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request), is_active=True)
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = tax + total
    context = {
        'total': total,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'total_quantity': quantity,
        'tax': tax
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request):
    total = quantity = 0
    current_user = request.user
    # cart = Cart.objects.get(cart_id=_cart_id(request))
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request), is_active=True)

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = tax + total
    context = {
        'total': total,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'total_quantity': quantity,
        'tax': tax
    }
    return render(request, 'store/checkout.html', context)
