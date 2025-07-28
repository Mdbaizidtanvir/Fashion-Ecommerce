
from django.urls import path
from app import views
from django.contrib.auth import views as auth_views
from .forms import CustomLoginForm
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.Home,name="home"),
        path('store', views.store,name="store"),
        path('about', views.about,name="about"),

           path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
path('update-cart/<int:pk>/', views.update_cart, name='update_cart'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(
        template_name='auth/login.html',
        authentication_form=CustomLoginForm  # <-- use custom form
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    path('orders/', views.my_orders, name='orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/delete/<int:order_id>/', views.delete_order, name='delete_order'),


    path('create-checkout-session/', views.create_checkout_session, name='stripe_checkout'),
    path('checkout/success/<str:order_id>/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('checkout/info/', views.checkout_info, name='checkout_info'),


    path('favorites/', views.favorites_list, name='favorites'),
    path('favorites/add/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),

path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),


path('my-returns/', views.return_requests_list, name='return_requests'),
    path('return-request/', views.create_return_request, name='create_return_request'),


]
