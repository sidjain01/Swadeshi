from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password

from django.views.decorators.csrf import csrf_exempt
from paytm import Checksum
MERCHANT_KEY = 'hahahahahaha'

from .models import User, Product, Order, Order_item, Shipping_Address, Coupon_Dis

# Create your views here.
query_result = []

# landing page
def landing_page(request):
    return render(request, 'landing/index.html')

def contact_page(request):
    return render(request, 'landing/contact.html')
# ----- Login/Signup ------

def login_user(request):
    if request.method == 'POST' :
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        print(user)
        if user is not None and user.is_customer:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Email password incorrect!')
            return redirect('login')
    else:
        if request.user.is_authenticated and request.user.is_customer:
            return redirect('home')
        return render(request, 'shop/login.html')
    
def logout_user(request):
    if request.user.is_authenticated and request.user.is_customer:
        logout(request)
        return redirect('home')
    else:
        return redirect('login') 

def register(request):
    if request.method == 'POST' :
        name = request.POST['name']
        mobile = request.POST['mobile']
        password = request.POST['password']
        email = request.POST['email']

        if User.objects.filter(email = email).exists():
            return render(request, 'shop/signup.html', {"errmsg": "You already have an account"})
        if User.objects.filter(mobile = mobile).exists():
            return render(request, 'shop/signup.html', {"errmsg": "Mobile No. already taken"})
        password = make_password(password)
        user = User.objects.create(name = name, mobile= mobile, is_customer= True, password= password, email= email)
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'shop/signup.html')


# ----- Basic ------

def home(request):
    products = Product.objects.all()
    categories = set()
    prod_category = {}
    prod_list = []
    for product in products:
        if(prod_category.get(product.category)):
            prod_category[product.category].append(product)
        else:
            prod_category[product.category] = [product]
    for category, products in prod_category.items():
        prod_list.append([category, products])

    # print(prod_category)
    return render(request, 'shop/landing.html',{'prod_list':prod_list})

def search(request):
    value = request.GET.get('search')
    value = value.lower()
    products = Product.objects.all()
    val_sp = value.split(" ")
    categories = set()
    name_prod = []
    cat_prod = []
    desc_prod = []
    query_result = []
    for product in products:
        if value in product.name.lower():
            name_prod.append(product)
            categories.add(product.category)
        else: 
            for val in val_sp:
                if val in product.category.name.lower():
                    cat_prod.append(product)
                    categories.add(product.category)
                elif val in product.description.lower():
                    desc_prod.append(product)
                    categories.add(product.category)
    
    query_result = name_prod + cat_prod + desc_prod
    categories_l = list(categories)
    return render(request, 'shop/products.html',{'search':value, 'prod_list':query_result,
     'categories':categories_l})

def single_product(request, prod_id):
    if request.method=='GET':
        prod = Product.objects.get(id = prod_id)
        return render(request, 'shop/single.html', {'product': prod})

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')

def my_orders(request):
    if request.user.is_authenticated and request.user.is_customer:
        orders= Order.objects.filter(user_id = request.user, completed = True)
        all_order_items = []
        order_id = 0
        if orders:
            for order in orders:
                items = Order_item.objects.filter(order_id = order)
                all_order_items.append([order, items])
        return render(request, 'shop/myorder.html', {"order_items": all_order_items, "order_id": order_id})
    else:
        return redirect('login')


# ----- Cart ------

def cart(request):
    if request.user.is_authenticated and request.user.is_customer:
        obj= Order.objects.filter(user_id = request.user, completed = False)
        items = []
        order_id = 0
        if obj:
            items = Order_item.objects.filter(order_id = obj[0])
            order_id = obj[0].order_id
        return render(request, 'shop/cart.html', {"items": items, "order_id": order_id})
    else:
        return redirect('login') 

def add_to_cart(request, prod_id):
    if request.user.is_authenticated and request.user.is_customer:
        if request.method=='GET':
            prod = Product.objects.get(id = prod_id)
            obj, created = Order.objects.get_or_create(user_id = request.user, completed = False)
            order_item, is_created = Order_item.objects.get_or_create(order_id = obj, prod_id = prod)
            if is_created == False:
                order_item.quantity = order_item.quantity +1
            order_item.save()
            return redirect('cart')
    else:
        return redirect('login')

def remove_from_cart(request, prod_id):
    if request.user.is_authenticated and request.user.is_customer:
        prod = Product.objects.get(id = prod_id)
        obj = Order.objects.get(user_id = request.user, completed = False)
        order_item = Order_item.objects.filter(order_id = obj, prod_id = prod)
        order_item[0].delete()
        return redirect('cart')
    else:
        return redirect('login')

def update_quantity_minus(request, orderitem_id):
    if request.user.is_authenticated and request.user.is_customer:
        order_item = Order_item.objects.filter(id = orderitem_id)
        if order_item and order_item[0].quantity>1:
            order_item[0].quantity = order_item[0].quantity -1
            order_item[0].save()
        return redirect('cart')
    else:
        return redirect('login')

def update_quantity_plus(request, orderitem_id):
    if request.user.is_authenticated and request.user.is_customer:
        order_item = Order_item.objects.filter(id = orderitem_id)
        if order_item:
            order_item[0].quantity = order_item[0].quantity + 1
            order_item[0].save()
        return redirect('cart')
    else:
        return redirect('login')

def apply_coupon(request):
    if request.user.is_authenticated and request.user.is_customer:
        if request.method == 'POST':
            coupon_code = request.POST.get('coupon').upper()
            if coupon_code is not None:
                coupon = Coupon_Dis.objects.filter(coupon_code=coupon_code)
                if coupon.exists():
                    order = Order.objects.filter(user_id=request.user, completed=False)
                    if order.exists():
                        order.update(coupon=coupon[0])
                        return redirect('cart')
                    else:
                        messages.info(request,"Try after adding items in the Cart!")
                        return redirect('cart')
                else:
                    order = Order.objects.filter(user_id=request.user, completed=False)
                    if order.exists():
                        order.update(coupon=None)
                    return redirect('cart')
            else:
                messages.info(request,"Enter valid coupon code!")
                return redirect('cart')
        else:
            return redirect('cart')
    else:
        return redirect('login')


# ----- Checkout ------

def payment(request):
    if request.user.is_authenticated and request.user.is_customer:
        if request.method == 'POST':
            pay = request.POST.get('paymentMethod')
            if pay == "paydel":
                order = Order.objects.filter(user_id=request.user, completed=False)[0]
                order.completed=True
                order.trans_mode="D"
                order.save()
                response_dict={
                    'ORDERID' : str(order.order_id),
                    'STATUS' : 'TXN_SUCCESS'
                }
                return render(request, 'shop/complete.html', {'response': response_dict})
            else:
                order = Order.objects.filter(user_id=request.user, completed=False)[0]
                param_dict ={
                    'MID':'WorldP64425807474247',
                    'ORDER_ID': str(order.order_id),
                    'TXN_AMOUNT': str(order.totalamt),
                    'CUST_ID': request.user.email,
                    'INDUSTRY_TYPE_ID':'Retail',
                    'WEBSITE':'WEBSTAGING',
                    'CHANNEL_ID':'WEB',
                    'CALLBACK_URL':'http://localhost:8000/handlepayment/',
                }
                param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict,MERCHANT_KEY) 
                return render(request, 'shop/paytm.html', {'param_dict':param_dict})
        return redirect('checkout')
    else:
        return redirect('login')

@csrf_exempt
def handlepayment(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            order_id = int(response_dict['ORDERID'])
            order = Order.objects.get(order_id=order_id)
            order.completed=True
            order.trans_mode="P"
            order.transaction_id=response_dict['TXNID']
            order.save()
            return render(request, 'shop/complete.html', {'response': response_dict})            
        else:
            return render(request, 'shop/complete.html', {'response': response_dict})            
    else:
        return redirect('cart')

def shipping_address(request):
    if request.user.is_authenticated and request.user.is_customer:
        if request.method=='POST':
            address = None
            if request.POST.get('addressid'):
                address_id = request.POST.get('addressid')
                address = Shipping_Address.objects.get(id=address_id)       
            else:
                full_name = request.POST['full_name']
                mobile = request.POST['mobile']
                pincode = request.POST['pincode']
                address = request.POST['address']
                city = request.POST['city']
                state = request.POST['state']

                address = Shipping_Address.objects.create(user_id= request.user, full_name = full_name, mobile= mobile,
                pincode= pincode, address= address, city= city, state= state)
                address.save()

            order = Order.objects.get(user_id = request.user, completed = False)
            order.shipping = address
            order.save()
            # login(request, user)
            return render(request, 'shop/payment.html')
        else: 
            addresses = Shipping_Address.objects.filter(user_id= request.user)
            return render(request, 'shop/deliver.html', {"addresses": addresses})
    else:
        return redirect('login')

def checkout(request):
    if request.user.is_authenticated and request.user.is_customer:
        if request.method == 'POST':
            totalamt = request.POST.get('totalamt')
            totalamt = int(totalamt)
            order = Order.objects.filter(user_id=request.user, completed=False)
            order.update(totalamt=totalamt)
            return redirect('deliver')
        return redirect('cart')
    else:
        return redirect('login')
