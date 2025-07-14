
from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from app.models import Contact, OrderItem, Tour
from .forms import TourForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from app.models import Order
from django.db.models import Count,Sum
from django.views.decorators.http import require_POST



def dashboard_view(request):
    return render(request, 'adminpage/dashboard.html')
def home_tour(request):
    return render(request,'adminpage/tour.html')

from django.core.exceptions import ValidationError
from django.utils import timezone

@staff_member_required
def qlall_tour_view(request):
    if request.method == 'POST':
        tour_id = request.POST.get('tour_id')
        name = request.POST.get('name')
        code = request.POST.get('code')
        price = request.POST.get('price')
        duration = request.POST.get('duration_days')
        start_date = request.POST.get('start_date')
        describe = request.POST.get('describe')
        image = request.FILES.get('image')

        if not all([name, code, price, duration, start_date, describe]):
            messages.error(request, "❌ Vui lòng nhập đầy đủ thông tin.")
            return redirect('qlall_tour')

        if start_date < str(timezone.now().date()):
            messages.error(request, "❌ Ngày bắt đầu phải từ hôm nay trở đi.")
            return redirect('qlall_tour')

        if tour_id:  # Sửa
            tour = get_object_or_404(Tour, id=tour_id)
            tour.name = name
            tour.code = code
            tour.price = price
            tour.duration_days = duration
            tour.start_date = start_date
            tour.describe = describe
            if image:
                tour.image = image
            tour.save()
            messages.success(request, "✅ Đã cập nhật Tour.")
        else:  # Thêm
            Tour.objects.create(
                name=name,
                code=code,
                price=price,
                duration_days=duration,
                start_date=start_date,
                describe=describe,
                image=image
            )
            messages.success(request, "✅ Đã thêm Tour mới.")

        return redirect('qlall_tour')

    today = date.today()
    tours = Tour.objects.all().order_by('-id')

    # ✅ Tour quá hạn chưa ai đặt (có start_date < hôm nay và không có đơn)
    tours_qua_han = Tour.objects.annotate(so_luot_dat=Count('orderitems')) \
    .filter(start_date__lt=today, so_luot_dat=0)

    return render(request, 'adminpage/qlall_tour.html', {
        'tours': tours,
        'tours_qua_han': tours_qua_han
    })

@staff_member_required
def xoa_tour(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    tour.delete()
    messages.success(request, "Đã xoá tour.")
    return redirect('qlall_tour')

from decimal import Decimal
from app.models import Order

def don_thanh_toan_view(request):
    orders = Order.objects.filter(status__in=['paid', 'waiting_payment']) \
        .select_related('customer') \
        .prefetch_related('items', 'items__tour')

    processed_orders = []

    for order in orders:
        user = order.customer
        username = user.username if user else "(Đã xoá)"

        total = sum(item.total_price or 0 for item in order.items.all())

        # ❗ Không dùng "or 100" vì nếu đã chọn 20 mà lưu sai → lỗi
        payment_percent = order.payment_percent if order.payment_percent is not None else 100
        percent_decimal = Decimal(payment_percent) / Decimal(100)

        paid_amount = (Decimal(total) * percent_decimal).quantize(Decimal('1'))
        remaining_amount = Decimal(total) - paid_amount

        processed_orders.append({
            'id': order.id,
            'username': username,
            'created_at': order.created_at,
            'payment_percent': payment_percent,
            'payment_method': order.payment_method,
            'total': total,
            'paid': paid_amount,
            'remain': remaining_amount,
            'tour_items': order.items.all()
        })

    return render(request, 'adminpage/ql_don_thanh_toan.html', {
        'orders': processed_orders,
        'total_orders': len(processed_orders),
    })





def trang_thai_tour_dang_mua(request):
    today = date.today()
    items = OrderItem.objects.select_related('order', 'tour').all()

    danh_sach_don = []

    for item in items:
        tour = item.tour
        order = item.order

        # Tính ngày kết thúc
        end_date = tour.start_date + timedelta(days=tour.duration_days)

        # Xác định trạng thái chính xác
        if today < tour.start_date:
            trang_thai = "Sắp bắt đầu"
        elif tour.start_date <= today < end_date:
            trang_thai = "Đang diễn ra"
        else:
            trang_thai = "Đã kết thúc"

        danh_sach_don.append({
            'ma_don': order.id,
            'ma_tour': tour.code,
            'ten_tour': tour.name,
            'trang_thai': trang_thai,
            'ngay_bat_dau': tour.start_date,
            'ly_do_huy': tour.ly_do_huy if hasattr(tour, 'ly_do_huy') else None 
        })

    return render(request, 'adminpage/trang_thai_mua_tour.html', {
        'danh_sach_don': danh_sach_don,
    })

# views.py

from app.forms import ContactForm, PlaceForm, FoodForm, CultureForm
from app.models import Place, Food, Culture
from django.contrib import messages

def ql_place(request):
    places = Place.objects.all()
    form = PlaceForm()

    # THÊM hoặc SỬA
    if request.method == 'POST':
        if 'edit_id' in request.POST:
            place = get_object_or_404(Place, id=request.POST.get('edit_id'))
            form = PlaceForm(request.POST, request.FILES, instance=place)
            if form.is_valid():
                form.save()
                messages.success(request, "Cập nhật địa danh thành công!")
                return redirect('ql_place')
        else:
            form = PlaceForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Thêm địa danh thành công!")
                return redirect('ql_place')

    return render(request, 'adminpage/ql_place.html', {'form': form, 'places': places})

def delete_place(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    place.delete()
    messages.success(request, "Đã xóa địa danh.")
    return redirect('ql_place')

# -------- QUẢN LÝ FOOD --------
def ql_food(request):
    foods = Food.objects.all()
    form = FoodForm()

    if request.method == 'POST':
        if 'edit_id' in request.POST:
            food = get_object_or_404(Food, id=request.POST.get('edit_id'))
            form = FoodForm(request.POST, request.FILES, instance=food)
            if form.is_valid():
                form.save()
                messages.success(request, "Cập nhật món ăn thành công!")
                return redirect('ql_food')
        else:
            form = FoodForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Thêm món ăn thành công!")
                return redirect('ql_food')

    return render(request, 'adminpage/ql_food.html', {'form': form, 'foods': foods})

def delete_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    food.delete()
    messages.success(request, "Đã xóa món ăn.")
    return redirect('ql_food')

# -------- QUẢN LÝ CULTURE --------
def ql_culture(request):
    cultures = Culture.objects.all()
    form = CultureForm()

    if request.method == 'POST':
        if 'edit_id' in request.POST:
            culture = get_object_or_404(Culture, id=request.POST.get('edit_id'))
            form = CultureForm(request.POST, request.FILES, instance=culture)
            if form.is_valid():
                form.save()
                messages.success(request, "Cập nhật nội dung văn hóa thành công!")
                return redirect('ql_culture')
        else:
            form = CultureForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Thêm nội dung văn hóa thành công!")
                return redirect('ql_culture')

    return render(request, 'adminpage/ql_culture.html', {'form': form, 'cultures': cultures})

def delete_culture(request, culture_id):
    culture = get_object_or_404(Culture, id=culture_id)
    culture.delete()
    messages.success(request, "Đã xóa nội dung văn hóa.")
    return redirect('ql_culture')


def admin_contacts(request):
    contacts = Contact.objects.all().order_by('-created_at')
    return render(request, 'adminpage/ql_contact.html', {'contacts': contacts})

def contact_detail_ajax(request, id):
    contact = get_object_or_404(Contact, id=id)
    return render(request, 'adminpage/contact_detail_ajax.html', {'contact': contact})

@csrf_exempt
def reply_contact_ajax(request, id):
    contact = get_object_or_404(Contact, id=id)
    if request.method == 'POST':
        reply = request.POST.get('reply')
        contact.reply = reply
        contact.is_replied = True
        contact.save()
    return render(request, 'adminpage/contact_detail_ajax.html', {'contact': contact})
def xoa_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    messages.success(request, "Đã xóa liên hệ.")
    return redirect('ql_contact')


@require_POST
@staff_member_required
def huy_tour_view(request):
    order_id = request.POST.get('order_id')
    ly_do = request.POST.get('ly_do_huy')

    order = get_object_or_404(Order, id=order_id)
    order.trang_thai = "Đã hủy"
    order.ly_do_huy = ly_do
    order.save()

    messages.success(request, f"Đã hủy đơn #{order.id} - {ly_do}")
    return redirect('trang_thai_mua_tour')

def tong_ngan_sach_view(request):
    orders = Order.objects.prefetch_related('items__tour')

    tong_don = orders.count()
    so_tour_da_ban = OrderItem.objects.aggregate(tong=Sum('quantity'))['tong'] or 0

    tong_tien = 0
    tong_thu_duoc = 0
    tong_con_no = 0
    tong_huy = 0

    for order in orders:
        total = sum(item.total_price for item in order.items.all())
        percent = Decimal(order.payment_percent) / Decimal(100)
        paid = total * percent
        remain = total - paid

        tong_tien += total
        tong_thu_duoc += paid

        if order.payment_percent < 100:
            tong_con_no += remain

        if order.status == "cancelled":
            tong_huy += paid  # hoặc total nếu bạn muốn tính cả tour chưa trả

    tong_ngan_sach = tong_thu_duoc - tong_huy

    return render(request, 'adminpage/tong_ngan_sach.html', {
        'tong_don': tong_don,
        'so_tour_da_ban': so_tour_da_ban,
        'tong_tien': tong_tien,
        'tong_thu_duoc': tong_thu_duoc,
        'tong_con_no': tong_con_no,
        'tong_huy': tong_huy,
        'tong_ngan_sach': tong_ngan_sach,
    })
@staff_member_required
@require_POST
def xoa_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    ten_nguoi_gui = contact.user.username if contact.user else contact.name or "Không rõ"

    contact.delete()
    messages.success(request, f"❌ Đã xoá liên hệ từ {ten_nguoi_gui}.")
    return redirect('ql_contact')

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.contrib.postgres.aggregates import ArrayAgg


from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class UserListAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Không dùng ArrayAgg (không hỗ trợ trên SQLite)
        normal_users = []
        for u in User.objects.filter(is_superuser=False):
            normal_users.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_staff': u.is_staff,
                'group_names': list(u.groups.values_list('name', flat=True))
            })

        admin_users = list(
            User.objects.filter(is_superuser=True)
            .values('id', 'username', 'email', 'is_staff')
        )

        all_groups = list(Group.objects.values('id', 'name'))

        return Response({
            'normal_users': normal_users,
            'admin_users': admin_users,
            'all_groups': all_groups
        })



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def group_list_api(request):
    return Response(list(Group.objects.all().values('id','name')))

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_action_api(request):
    uid = request.data.get('id')
    action = request.data.get('action')
    user = get_object_or_404(User, pk=uid)

    if action == 'delete':
        if user.is_superuser:
            return Response({'error': 'Không thể xoá Admin chính'}, status=400)
        user.delete()

    elif action == 'toggle_staff':
        # không cho admin chính toggle
        if user.is_superuser and not request.user.is_superuser:
            return Response({'error': 'Không có quyền'}, status=403)
        user.is_staff = not user.is_staff
        user.save()

    elif action in ['add_group','remove_group']:
        group = get_object_or_404(Group, name=request.data.get('group'))
        if action == 'add_group':
            user.groups.add(group)
        else:
            user.groups.remove(group)

    else:
        return Response({'error':'Action không hợp lệ'}, status=400)

    return Response({'ok': True})
# views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

class ManageUsersView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'adminpage/manage_users.html'

    def test_func(self):
        return self.request.user.is_staff  # hoặc .is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Bạn không có quyền truy cập")
