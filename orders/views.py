from django.shortcuts import render, redirect
from carts.models import CartItem
from django.contrib.auth.decorators import login_required
from .models import Order
from .forms import OrderForm
import datetime


@login_required(login_url='login')
def payments(request):
    return render(request, 'orders/payments.html')


# Create your views here.
def place_order(request, total=0, quantity=0):
    # current_user =
    # return render(request, )
    current_user = request.user

    # if the cart count is less than or equal to 0, then redirect bac to shop

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = tax + total

    if request.method == "POST":
        print("post")
        form = OrderForm(request.POST)
        # print(form.cleaned_data['first_namwe'])
        if form.is_valid():
            print('valid')
            # store al the billing in for inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.phone_number = form.cleaned_data['phone_number']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'grand_total': grand_total,
                'tax': tax,
                'total': total,
            }
            return render(request, 'orders/payments.html',context)

    return redirect('checkout')
