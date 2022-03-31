from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Customer, Product, Cart, OrderPlaced, CATEGORY_CHOICES
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ProductView(View):
    def get(self, request):
        totalitem = 0
        laptops = Product.objects.filter(category='L')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html',
                      {'laptops': laptops, 'bottomwears': bottomwears, 'mobiles': mobiles, 'totalitem': totalitem})


class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        print(product.id)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html',
                      {'product': product, 'item_already_in_cart': item_already_in_cart, 'totalitem': totalitem})


@login_required()
def add_to_cart(request):
    user = request.user
    item_already_in_cart1 = False
    product = request.GET.get('prod_id')
    item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()
    if item_already_in_cart1 == False:
        product_title = Product.objects.get(id=product)
        Cart(user=user, product=product_title).save()
        messages.success(request, 'Product Added to Cart Successfully !!')
        return redirect('/cart')
    else:
        return redirect('/cart')


# Below Code is used to return to same page
# return redirect(request.META['HTTP_REFERER'])

@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        user = request.user
        cart = Cart.objects.filter(user=request.user)
        amount = 0.0
        shipping_amount = 70.0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
            totalamount = amount + shipping_amount
            ttamount = (p.quantity * p.product.discounted_price)
            return render(request, 'app/addtocart.html',
                          {'carts': cart, 'amount': amount, 'totalamount': totalamount, 'totalitem': totalitem,
                           'ttamount': ttamount})
        else:
            return render(request, 'app/emptycart.html', {'totalitem': totalitem})
    else:
        return render(request, 'app/emptycart.html', {'totalitem': totalitem})


# def plus_cart(request, id):
#     if request.method == 'GET':
#         prod_id = request.GET['id']
#         c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
#         c.quantity += 1
#         c.save()
#         amount = 0.0
#         shipping_amount = 70.0
#         cart_product = [p for p in Cart.objects.all() if p.user == request.user]
#         for p in cart_product:
#             tempamount = (p.quantity * p.product.discounted_price)
#             amount += tempamount
#         data = {
#             'quantity': c.quantity,
#             'amount': amount,
#             'totalamount': amount + shipping_amount
#         }
#         return JsonResponse(data)
#     else:
#         return HttpResponse("")
#
#
# def minus_cart(request, id):
#     if request.method == 'GET':
#         prod_id = request.GET['id']
#         c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
#         c.quantity -= 1
#         c.save()
#         amount = 0.0
#         shipping_amount = 70.0
#         cart_product = [p for p in Cart.objects.all() if p.user == request.user]
#         for p in cart_product:
#             tempamount = (p.quantity * p.product.discounted_price)
#             amount += tempamount
#         data = {
#             'quantity': c.quantity,
#             'amount': amount,
#             'totalamount': amount + shipping_amount
#         }
#         return JsonResponse(data)
#     else:
#         return HttpResponse("")


@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=request.user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add': add, 'cart_items': cart_items, 'totalcost': totalamount})


@login_required
def payment_done(request):
    custid = request.GET.get('custid')
    user = request.user
    cartid = Cart.objects.filter(user=user)
    customer = Customer.objects.get(id=custid)
    print(custid)
    for cid in cartid:
        OrderPlaced(user=user, customer=customer, product=cid.product, quantity=cid.quantity).save()
        cid.delete()
    return redirect("orders")


def remove_cart(request, id):
    if request.user.is_authenticated:
        customer = request.user
        x = Product.objects.get(id=id)
        object = Cart.objects.filter(product=x, user=customer)
        object.delete()
    return redirect('/cart')


@login_required
def address(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary', 'totalitem': totalitem})


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed': op})


def mobile(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Redmi' or data == 'Samsung':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)
    return render(request, 'app/mobile.html', {'mobiles': mobiles, 'totalitem': totalitem})


def laptops(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        laptops = Product.objects.filter(category='L')
    elif data == 'Lenovo' or data == 'Dell':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'below':
        laptops = Product.objects.filter(category='L').filter(discounted_price__lt=10000)
    elif data == 'above':
        laptops = Product.objects.filter(category='L').filter(discounted_price__gt=10000)
    return render(request, 'app/mobile.html', {'mobiles': laptops, 'totalitem': totalitem})


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulations!! Registered Successfully.')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'totalitem': totalitem})

    def post(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulations!! Profile Updated Successfully.')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'totalitem': totalitem})


def update_cart(request):

    if request.is_ajax() and request.method == "POST":
        products_id = request.POST.get('product_id')
        product_qty = request.POST.get('qty', 'None')
        item = Cart.objects.filter(Q(product_id=products_id) & Q(user=request.user)).first()
        amount = 0.0
        shipping_amount = 70.0
        tempamount = 0.0
        # totalamount = 0.0
        if item:
            item.quantity = product_qty
            print(product_qty, "hii")
            item.save()
            price = int(item.product.discounted_price) * int(item.quantity)
            cart_product = [p for p in Cart.objects.all() if p.user == request.user]
            print(cart_product, "Cart Product")
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                print(tempamount)
                print(p.quantity, "hello")
                amount += tempamount
                print(amount)
                totalamount = amount + shipping_amount
            return JsonResponse({'success': True, 'price': price, 'amount': amount, 'totalamount': totalamount})
        return JsonResponse({'success': False})


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            cart_items = Cart.objects.filter(user=request.user)
            op = OrderPlaced.objects.filter(user=request.user)
            ordpr = 0
            cartitm = 0

            for j in op:
                if j.id is not None:
                    ordpr += 1
                else:
                    ordpr = ordpr
            cat_name = []
            cat_qty = []
            for i in CATEGORY_CHOICES:
                print(i[0])
                cat_name.append(i[1])
                items = Cart.objects.filter(Q(user=request.user) & Q(product__category=i[0]))
                print(items)
                count = 0
                for j in items:
                    count = count + j.quantity
                cat_qty.append(count)
            print(cat_name)
            print(cat_qty)

            for i in cart_items:
                if i.product is not None:
                    cartitm += 1
        else:
            cart_items = Cart.objects.filter(user=request.user)
            op = OrderPlaced.objects.filter(user=request.user)
            ordpr = 0
            cartitm = 0

            for j in op:
                if j.id is not None:
                    ordpr += 1
                else:
                    ordpr = ordpr
            cat_name = []
            cat_qty = []
            for i in CATEGORY_CHOICES:
                print(i[0])
                cat_name.append(i[1])
                items = Cart.objects.filter(Q(user=request.user) & Q(product__category=i[0]))
                print(items)
                count = 0
                for j in items:
                    count = count + j.quantity
                cat_qty.append(count)
            print(cat_name)
            print(cat_qty)

            for i in cart_items:
                if i.product is not None:
                    cartitm += 1
    return render(request, 'app/dashboard.html',
                  {'cartitm': cartitm, 'cat_qty': cat_qty, 'cat_name': cat_name})


@login_required
def dash(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            product = Product.objects.all()
            order = OrderPlaced.objects.all()
            user = User.objects.all()
            productcount = 0
            ordercount = 0
            usercount = 0
            laptop = []
            topwear = []
            bottomwear = []
            phone = []
            for i in product:
                if i.id is not None:
                    productcount += 1
                else:
                    productcount = productcount
            ph, lt, t, b = 0, 0, 0, 0
            for l in product:
                if l.category == "M":
                    phone.append(l.category)
                    ph = phone.count("M")
                elif l.category == "L":
                    laptop.append(l.category)
                    lt = laptop.count("L")
                    print(lt)
                elif l.category == "TW":
                    topwear.append(l.category)
                    t = topwear.count("TW")
                else:
                    bottomwear.append(l.category)
                    b = bottomwear.count("BW")
                data = {"Phone": ph, "Laptop": lt, "TopWear": t, "BottomWear": b}
            for j in order:
                if j.id is not None:
                    ordercount += 1
                else:
                    ordercount = ordercount
            for k in user:
                if k.id is not None:
                    usercount += 1
                else:
                    usercount = usercount
        else:
            return redirect("userdash")
        return render(request, 'app/dashboard1.html',
                      {'data': data, 'order': order, 'user': user, 'productcount': productcount,
                       'ordercount': ordercount, 'usercount': usercount})


@login_required
def userdash(request):
    if request.user.is_authenticated:
        if request.user.is_authenticated is not request.user.is_superuser:
            cart_items = Cart.objects.filter(user=request.user)
            op = OrderPlaced.objects.filter(user=request.user)
            ordpr = 0
            cartitm = 0

            for j in op:
                if j.id is not None:
                    ordpr += 1
                else:
                    ordpr = ordpr
            cat_name = []
            cat_qty = []
            for i in CATEGORY_CHOICES:
                print(i[0])
                cat_name.append(i[1])
                items = Cart.objects.filter(Q(user=request.user) & Q(product__category=i[0]))
                print(items)
                count = 0
                for j in items:
                    count = count + j.quantity
                cat_qty.append(count)
            print(cat_name)
            print(cat_qty)

            for i in cart_items:
                if i.product is not None:
                    cartitm += 1
        else:
            return redirect("dashboard1")
        return render(request, 'app/userdash.html', {'cartitm': cartitm, 'cat_qty': cat_qty, 'cat_name': cat_name})
