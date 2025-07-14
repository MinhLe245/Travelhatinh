from django.utils import timezone
from django.shortcuts import render,redirect
from .models import Contact, Place, Food, Culture, Tour
from .forms import ContactForm, ReviewForm 
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .forms import SignUpForm
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator




def get_or_create_order_for_user(user):
    order, created = Order.objects.get_or_create(customer=user, status='pending')
    return order
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def send_invoice_email(order, full_name, email):
    subject = f"Xác nhận thanh toán Tour #{order.id}"
    body = render_to_string('app/email_invoice.html', {
        'order': order,
        'full_name': full_name,
    })
    email_msg = EmailMessage(subject, body, to=[email])
    email_msg.content_subtype = "html"  # Gửi dưới dạng HTML
    email_msg.send()


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # ✅ Check nhóm
            if user.groups.filter(name='AdminTravel').exists():
                return redirect('admin_dashboard')  # adminpage
            else:
                return redirect('home')  # người dùng thường

        else:
            messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu.')

    return render(request, 'app/login.html')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đăng ký thành công! Bạn có thể đăng nhập ngay.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'app/signup.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='AdminTravel').exists():
            return redirect('admin_dashboard')
    return render(request, 'app/home.html')

def place(request):
    places = Place.objects.all()
    return render(request, 'app/place.html', {'places': places})

def food(request):
    foods = Food.objects.all()
    return render(request, 'app/food.html', {'foods': foods})

def culture(request):
    cultures = Culture.objects.all()
    return render(request, 'app/culture.html', {'cultures': cultures})
def tour(request):
    tours = Tour.objects.all().order_by('id')
    paginator = Paginator(tours, 6)  # 6 tour mỗi trang

    # Lấy các giá trị từ form tìm kiếm
    duration = request.GET.get('duration')
    month = request.GET.get('month')
    year = request.GET.get('year')

    # Lọc theo các điều kiện nếu có
    if duration:
        tours = tours.filter(duration_days=int(duration))
    if month:
        tours = tours.filter(start_date__month=int(month))
    if year:
        tours = tours.filter(start_date__year=int(year))

    # Phân trang
    
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'app/tour.html', {
        'tours': page_obj.object_list,  # ✅ Quan trọng: chỉ lấy tour của trang hiện tại
        'searched': bool(duration or month or year),
        'page_obj': page_obj,
    })
@csrf_exempt
def tour_search_ajax(request):
    if request.method == 'POST':
        duration = request.POST.get('duration')
        month = request.POST.get('month')
        year = request.POST.get('year')
        page = request.POST.get('page')

        tours = Tour.objects.all()
        if duration:
            tours = tours.filter(duration_days=duration)
        if month:
            tours = tours.filter(start_date__month=month)
        if year:
            tours = tours.filter(start_date__year=year)

        paginator = Paginator(tours, 6)
        page_obj = paginator.get_page(page)

        html = render_to_string('app/tour_list.html', {
            'tours': page_obj.object_list,
            'page_obj': page_obj,
        }, request=request)  # ✅ THÊM request VÀO ĐÂY

        return HttpResponse(html)

    return HttpResponse("Không hợp lệ", status=400)



def contact(request):
    form = ContactForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        contact = form.save(commit=False)
        if request.user.is_authenticated:
            contact.user = request.user
        contact.save()
        return redirect('contact')  # hoặc render trang success
    return render(request, 'app/contact.html', {'form': form})


def review(request):
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        form.save()
        return render(request, 'app/review_success.html')
    return render(request, 'app/review.html', {'form': form})



@login_required
def buytour(request):
    # Tìm đơn hàng đang chờ của user
    order, created = Order.objects.get_or_create(
        customer=request.user,
        status='pending',
        defaults={'created_at': timezone.now()}
    )

    cart_tours = []
    total_people = 0
    total_price = 0

    for item in order.items.all():
        cart_tours.append({
            'tour': item.tour,
            'quantity': item.quantity,
            'total_price': item.total_price
        })
        total_people += item.quantity
        total_price += item.total_price

    return render(request, 'app/buytour.html', {
        'cart_tours': cart_tours,
        'total_people': total_people,
        'total_price': total_price,
    })


from django.db.models import Q

@login_required
def add_to_cart(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    # 👉 Xoá các đơn hàng 'pending' dư thừa nếu có nhiều hơn 1
    pending_orders = Order.objects.filter(customer=request.user, status='pending')
    if pending_orders.count() > 1:
        # Giữ đơn đầu tiên, xoá các đơn dư
        pending_orders.exclude(id=pending_orders.first().id).delete()

    # ✅ Lấy hoặc tạo đơn hàng mới
    order, _ = Order.objects.get_or_create(customer=request.user, status='pending')

    # 👉 Kiểm tra item đã có chưa
    item = OrderItem.objects.filter(order=order, tour=tour).first()

    if item:
        item.quantity += 1
    else:
        item = OrderItem(order=order, tour=tour, quantity=1)

    # 👉 Cập nhật tổng tiền
    item.total_price = item.quantity * tour.price
    item.save()

    # 👉 Điều hướng sau khi thêm
    next_url = request.GET.get('next', 'tour')
    return redirect(next_url)


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app.models import Tour, Order, OrderItem
from decimal import Decimal

@require_POST
@login_required
@csrf_protect
def add_to_cart_ajax(request):
    tour_id = request.POST.get('tour_id')
    try:
        tour = Tour.objects.get(id=tour_id)
    except Tour.DoesNotExist:
        return JsonResponse({'success': False, 'error': '❌ Tour không tồn tại'}, status=400)

    order = Order.objects.filter(customer=request.user, status='pending').first()
    if not order:
        order = Order.objects.create(customer=request.user, status='pending')

    # ❌ Không dùng get_or_create nữa
    item = OrderItem.objects.filter(order=order, tour=tour).first()

    if item:
        item.quantity += 1
    else:
        item = OrderItem(
            order=order,
            tour=tour,
            tour_name=tour.name,
            tour_code=tour.code,
            tour_price=tour.price,
            quantity=1
        )
    item.total_price = item.quantity * tour.price
    item.save()

    return JsonResponse({'success': True, 'message': '✅ Đã thêm tour vào giỏ!'})

@login_required
def update_cart(request):
    order = Order.objects.filter(customer=request.user, status='pending').first()
    if not order:
        return redirect('buytour')

    if request.method == 'POST':
        if 'increase' in request.POST:
            tour_id = request.POST.get('increase')
            item = order.items.filter(tour_id=tour_id).first()
            if item:
                item.quantity += 1
                item.save()

        elif 'decrease' in request.POST:
            tour_id = request.POST.get('decrease')
            item = order.items.filter(tour_id=tour_id).first()
            if item:
                item.quantity -= 1
                if item.quantity <= 0:
                    item.delete()
                else:
                    item.save()

    return redirect('buytour')

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Order

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

@login_required
def checkout(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        payment_method = request.POST.get('payment_method')

        # Lấy đơn hàng đang chờ
        order = Order.objects.filter(customer=request.user, status='pending').first()

        if order:
            order.status = "paid"
            order.payment_method = payment_method 
            order.payment_percent = 20 if payment_method == 'pay_20' else 100
            order.save()

            # Tính tổng tiền giỏ hàng
            total_price = sum(item.total_price for item in order.items.all())

            # Tính số tiền cần thanh toán
            if payment_method == 'pay_20':
                amount_to_pay = total_price * Decimal('0.2')
            else:
                amount_to_pay = total_price

            # Gửi email xác nhận (HTML)
            html_content = render_to_string('app/email_invoice.html', {
                'order': order,
                'full_name': full_name,
                'payment_method': payment_method,
                'amount_to_pay': amount_to_pay,
            })

            subject = "✅ Xác nhận đặt tour thành công"
            from_email = settings.EMAIL_HOST_USER
            to_email = [email]

            email_msg = EmailMultiAlternatives(subject, '', from_email, to_email)
            email_msg.attach_alternative(html_content, "text/html")
            try:
                email_msg.send()
            except Exception as e:
                print("❌ Lỗi gửi email:", e)

            # Lưu session để hiển thị ở trang thành công
            request.session['last_order_id'] = order.id
            request.session['full_name'] = full_name
            request.session['amount_to_pay'] = float(amount_to_pay)
            request.session['payment_method'] = payment_method

            return redirect('payment_success')

        else:
            return redirect('buytour')  # Không có đơn thì quay lại

    # Nếu GET: Hiển thị lại form
    order = Order.objects.filter(customer=request.user, status='pending').first()
    if not order:
        return redirect('buytour')

    return render(request, 'app/checkout.html', {
        'order': order
    })

from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import intcomma

def payment_success(request):
    order_id = request.session.get('last_order_id')
    full_name = request.session.get('full_name')
    amount_to_pay = request.session.get('amount_to_pay')
    payment_method = request.session.get('payment_method')

    order = Order.objects.filter(id=order_id).first()
    if not order:
        return redirect('buytour')

    return render(request, 'app/payment_success.html', {
        'order': order,
        'full_name': full_name,
        'amount_to_pay': Decimal(str(amount_to_pay)),  # ✅ truyền đúng kiểu Decimal
        'payment_method': payment_method,
    })

# views.py
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            if request.user.is_authenticated:
                contact.user = request.user
                contact.name = request.user.get_full_name() or request.user.username
                contact.email = request.user.email
            contact.save()
            messages.success(request, "✅ Đã gửi liên hệ!")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'app/contact.html', {'form': form})

@login_required
def your_tours(request):
    orders = Order.objects.filter(customer=request.user).exclude(status='pending').order_by('-created_at')
    return render(request, 'app/your_tours.html', {
        'orders': orders
    })


