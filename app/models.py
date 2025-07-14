from datetime import timedelta
from decimal import Decimal
from django.utils import timezone 
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import User

class Place(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    describe = models.TextField()
    image = models.ImageField(upload_to='places/')
    rating = models.FloatField(default=0.0) 
    def __str__(self):
        return self.name

class Food(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    describe = models.TextField()
    image = models.ImageField(upload_to='foods/')
    rating = models.FloatField(default=0.0)
    def __str__(self):
        return self.name
class Culture(models.Model):
    name = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    describe = models.TextField()
    image = models.ImageField(upload_to='cultures/')
    rating = models.FloatField(default=0.0) 
    def __str__(self):
        return self.name

class Tour(models.Model):
    name = models.CharField(max_length=255)
    describe = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='tours/')
    code = models.CharField(max_length=20, unique=True)
    ly_do_huy = models.TextField(null=True, blank=True)


    def clean(self):
        if self.start_date and self.duration_days:
            self.end_date = self.start_date + timedelta(days=int(self.duration_days))
        if self.start_date and self.start_date < timezone.now().date():
            raise ValidationError("Ngày bắt đầu tour phải từ hôm nay trở đi.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Gọi clean() để kiểm tra dữ liệu
        if self.start_date and self.duration_days:
            self.end_date = self.start_date + timedelta(days=int(self.duration_days))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)  # ✅ THÊM: Số điện thoại
    subject = models.CharField(max_length=200, blank=True, null=True)  # ✅ THÊM: Tiêu đề liên hệ
    message = models.TextField()
    image = models.ImageField(upload_to='contacts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Admin phản hồi
    reply = models.TextField(blank=True, null=True)
    reply_at = models.DateTimeField(blank=True, null=True)  # ✅ THÊM: thời điểm phản hồi
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.subject or 'Liên hệ'}] - {self.name or self.user.username}"



class Review(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 đến 5 sao
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('waiting_payment', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('cancelled', 'Đã hủy'),
    ]

    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    # Trạng thái đơn hàng
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Thông tin khách hàng
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)

    # Thanh toán
    payment_percent = models.PositiveIntegerField(default=100)  # Ví dụ: 20 hoặc 100
    payment_method = models.CharField(max_length=50, default='online')  # online / cash

    # Hủy đơn
    cancel_reason = models.TextField(blank=True, null=True)  # Lý do huỷ đơn (nếu có)
    cancelled_at = models.DateTimeField(blank=True, null=True)  # Thời gian huỷ (nếu có)

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.customer.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    tour = models.ForeignKey('Tour', on_delete=models.SET_NULL, null=True, blank=True, related_name='orderitems')

    # Lưu thông tin tour phòng khi tour bị xóa
    tour_name = models.CharField(max_length=255, null=True, blank=True)
    tour_code = models.CharField(max_length=100, null=True, blank=True)
    tour_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Gán thông tin từ tour nếu có
        if self.tour:
            self.tour_name = self.tour.name
            self.tour_code = self.tour.code
            self.tour_price = self.tour.price

        # Luôn tính lại total_price khi lưu
        if self.tour_price is not None and self.quantity:
            self.total_price = Decimal(self.quantity) * Decimal(self.tour_price)

        super().save(*args, **kwargs)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count, Max
from .models import OrderItem, Order, Review, Tour

class TourStatsAPIView(APIView):
    def get(self, request):
        completed = Order.objects.filter(status='paid').count()
        cancelled = Order.objects.filter(status='cancelled').count()
        avg_price = OrderItem.objects.aggregate(avg=Avg('tour_price'))['avg']
        top_tours = list(
            OrderItem.objects
            .values('tour_name')
            .annotate(total_rev=Max('tour_price'))
            .order_by('-total_rev')[:5]
        )
        positive = Review.objects.filter(rating__gte=4).count()
        negative = Review.objects.filter(rating__lte=3).count()
        return Response({
            "completed": completed,
            "cancelled": cancelled,
            "avg_price": float(avg_price or 0),
            "top_tours": top_tours,
            "ratings": {"positive": positive, "negative": negative}
        })



