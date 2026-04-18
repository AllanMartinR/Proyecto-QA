from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='store/password_reset.html',
        email_template_name='store/password_reset_email.html',
        success_url='/forgot-password/done/',
        form_class=CustomPasswordResetForm
    ), name='forgot_password'),
    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='store/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='store/password_reset_confirm.html',
        success_url='/reset-password/complete/',
        form_class=CustomSetPasswordForm
    ), name='reset_password'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='store/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('logout/', views.logout_view, name='logout'),
    path('add_product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    path('edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('add_category/', views.add_category, name='add_category'),
    path('categories/', views.category_list, name='category_list'),
    path('admin_menu/', views.admin_menu, name='admin_menu'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('user-category/<int:category_id>/', views.user_category_products, name='user_category_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
	path('edit_category/<int:pk>/', views.edit_category, name='edit_category'),
	path('delete_category/<int:pk>/', views.delete_category, name='delete_category'),
	path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),
	path('search/', views.search_results, name='search_results'),
	# Carrito
	path('cart/', views.cart_view, name='cart'),
	path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
	path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
	path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
	# Checkout y pedidos
	path('checkout/', views.checkout, name='checkout'),
	path('tracking/<int:pedido_id>/', views.tracking, name='tracking'),
	path('update-tracking/<int:pedido_id>/', views.update_tracking, name='update_tracking'),
	path('my-orders/', views.my_orders, name='my_orders'),
	# Gestión de usuarios
	path('users/', views.user_list, name='user_list'),
	path('delete-user/<int:pk>/', views.delete_user, name='delete_user'),
]