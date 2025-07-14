from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect

urlpatterns = [
    path('', views.home, name='home'), 
    path('login/', views.login_view,name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('', lambda request: redirect('login'), name='root'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('places/', views.place, name='place'), 
    path('foods/', views.food, name='food'),
    path('cultures/', views.culture, name='culture'),
    path('tours/', views.tour, name='tour'),
    path("tour/ajax/", views.tour_search_ajax, name="tour_search_ajax"),
    path('contacts/', views.contact, name='contact'),
    path('reviews/', views.review, name='review'),
    path('buytour/', views.buytour, name='buytour'),
    path('add-to-cart/<int:tour_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('api/add-to-cart/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.payment_success, name='payment_success'),
    path('lien-he/', views.contact_view, name='lien_he'),
    path('your-tours/', views.your_tours, name='your_tours'),




]
