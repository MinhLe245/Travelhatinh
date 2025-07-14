from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='admin_dashboard'),
    path('hometour/', views.home_tour, name='hometour'),

    # ✅ Một URL duy nhất cho danh sách + thêm + sửa
    path('admin/tour/', views.qlall_tour_view, name='qlall_tour'),
    # ✅ Xóa vẫn cần riêng
    path('admin/tour/delete/<int:tour_id>/', views.xoa_tour, name='xoa_tour'),

    path('admin/don-thanh-toan/', views.don_thanh_toan_view, name='don_thanh_toan'),
    path('admin/trang-thai-mua-tour/',views.trang_thai_tour_dang_mua, name='trang_thai_mua_tour'),

    path('quan-ly-dia-danh/', views.ql_place, name='ql_place'),
    path('xoa-dia-danh/<int:place_id>/', views.delete_place, name='delete_place'),
 
    path('quan-ly-am-thuc/', views.ql_food, name='ql_food'),
    path('xoa-am-thuc/<int:food_id>/', views.delete_food, name='delete_food'),

    path('quan-ly-van-hoa/', views.ql_culture, name='ql_culture'),
    path('xoa-van-hoa/<int:culture_id>/', views.delete_culture, name='delete_culture'),

    path('quan-ly-lien-he/', views.admin_contacts, name='ql_contact'),
    path('chi-tiet-lien-he/<int:id>/', views.contact_detail_ajax, name='contact_detail_ajax'),
    path('phan-hoi/<int:id>/', views.reply_contact_ajax, name='reply_contact_ajax'),
    path('xoa-lien-he/<int:id>/', views.xoa_contact, name='xoa_contact'),


    path('admin/huy-tour/', views.huy_tour_view, name='huy_tour'),
    path('admin/tong-ngan-sach/', views.tong_ngan_sach_view, name='tong_ngan_sach'),


    path('manage-users/', views.ManageUsersView.as_view(), name='manage-users'),
    path('api-users/', views.UserListAPI.as_view(), name='api-users'),
    path('api-users-action/', views.user_action_api, name='api-users-action'),
    path('api/groups/', views.group_list_api, name='api-groups'),








]
