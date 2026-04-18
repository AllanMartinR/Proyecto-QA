from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.db.models import Count, Q
import random
from store.models import CustomUser, Product, Category, Cart, CartItem, Pedido, PedidoItem, PEDIDO_ESTADOS
import logging
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProductForm, CategoryForm
from django.contrib.auth import logout as auth_logout
from datetime import datetime, timedelta
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        logger.info(f"Intentando autenticar con username: {username}, password: {password}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            logger.info(f"Usuario autenticado: {user}, is_staff: {user.is_staff}")
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso.')
            if user.is_staff:
                logger.info("Redirigiendo a admin_menu")
                return redirect('/admin_menu/')  # Usamos URL absoluta como prueba
            logger.info("Redirigiendo a home")
            return redirect('home')
        else:
            logger.info(f"Autenticación fallida para username: {username}")
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Contraseña incorrecta.')
            else:
                messages.error(request, 'El usuario no está registrado.')
    return render(request, 'store/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya está registrado.')
        else:
            user = CustomUser.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión.')
            return redirect('login')
    return render(request, 'store/register.html')

def search_results(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()
    
    # Filtro por precio
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass
    
    # Ordenar por precio
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')
    
    # Obtener carrito si el usuario está autenticado
    cart = None
    if request.user.is_authenticated:
        cart = get_or_create_cart(request.user)

    return render(request, 'store/search_results.html', {
        'query': query,
        'products': products,
        'result_count': products.count(),
        'cart': cart
    })
	
def home_view(request):
    # Si el usuario es staff, redirigir al admin_menu
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_menu')

    # Obtener 4 productos ALEATORIOS
    products = list(Product.objects.all())
    featured_products = random.sample(products, min(4, len(products))) if products else []

    # Pasar categorías al menú desplegable
    categories = Category.objects.all()
    
    # Obtener carrito si existe (solo si está autenticado)
    cart = None
    if request.user.is_authenticated:
        cart = get_or_create_cart(request.user)

    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'cart': cart
    })

def logout_view(request):
    auth_logout(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('home')


def is_admin(user):
    return user.is_authenticated and user.is_staff



@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado exitosamente.")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado exitosamente.")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/edit_product.html', {'form': form, 'product': product})

@login_required
@user_passes_test(is_admin)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Producto '{product.name}' eliminado exitosamente.")
        return redirect('product_list')
    return render(request, 'store/delete_product.html', {'product': product})


@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría agregada exitosamente.")
            return redirect('category_list')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = CategoryForm()
    return render(request, 'store/add_category.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada exitosamente.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'store/edit_category.html', {'form': form, 'category': category})

@login_required
@user_passes_test(is_admin)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Categoría eliminada exitosamente.")
        return redirect('category_list')
    return render(request, 'store/delete_category.html', {'category': category})

# Vistas de gestión de usuarios
@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'store/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def delete_user(request, pk):
    user_to_delete = get_object_or_404(CustomUser, pk=pk)
    
    # Prevenir que un administrador se elimine a sí mismo
    if user_to_delete == request.user:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"Usuario '{username}' eliminado exitosamente.")
        return redirect('user_list')
    return render(request, 'store/delete_user.html', {'user': user_to_delete})

def category_products(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category)
    
    # Filtro por precio
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass
    
    # Ordenar por precio
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')
    
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def user_category_products(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category)
    
    # Filtro por precio
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass
    
    # Ordenar por precio
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')
    
    # Obtener carrito solo si está autenticado
    cart = None
    if request.user.is_authenticated:
        cart = get_or_create_cart(request.user)
    
    return render(request, 'store/user_category_products.html', {
        'category': category,
        'products': products,
        'cart': cart
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
@user_passes_test(is_admin)
def admin_menu(request):
    categories = Category.objects.all()
    return render(request, 'store/admin_menu.html', {'categories': categories})

# Funciones auxiliares para el carrito
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

# Vistas del carrito
def cart_view(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para acceder al carrito de compras.')
        return redirect('login')
    
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.all()
    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total()
    })

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect('login')
    
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        cart = get_or_create_cart(request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(request, f'No hay suficiente stock disponible. Stock actual: {product.stock}')
                return redirect('product_detail', product_id=product_id)
        
        messages.success(request, f'Producto agregado al carrito: {product.name}')
        # Mantener al usuario en la misma página usando HTTP_REFERER
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('home')
    return redirect('home')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(request, 'No hay suficiente stock disponible')
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()
            messages.success(request, 'Producto eliminado del carrito')
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, 'Producto eliminado del carrito')
    return redirect('cart')

# Vista de checkout
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para realizar una compra.')
        return redirect('login')
    
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('cart')
    
    if request.method == 'POST':
        # Crear pedido
        pedido = Pedido.objects.create(
            user=request.user,
            total=cart.get_total(),
            nombre_completo=request.POST.get('nombre_completo'),
            email=request.POST.get('email'),
            telefono=request.POST.get('telefono'),
            direccion=request.POST.get('direccion'),
            ciudad=request.POST.get('ciudad'),
            codigo_postal=request.POST.get('codigo_postal'),
            numero_tarjeta=request.POST.get('numero_tarjeta', '')[:4] + '****' if request.POST.get('numero_tarjeta') else '',
            fecha_expiracion=request.POST.get('fecha_expiracion', ''),
            cvv='***'
        )
        
        # Crear items del pedido
        for cart_item in cart_items:
            PedidoItem.objects.create(
                pedido=pedido,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            # Reducir stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Limpiar carrito
        cart.items.all().delete()
        
        messages.success(request, f'Pedido realizado exitosamente. Número de pedido: {pedido.numero_pedido}')
        return redirect('tracking', pedido_id=pedido.id)
    
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total()
    })

# Vista de tracking
@login_required
def tracking(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, user=request.user)
    # Avanzar estado si es necesario
    advance_order_status(pedido)
    pedido.refresh_from_db()
    estados = PEDIDO_ESTADOS
    current_index = next((i for i, (code, _) in enumerate(estados) if code == pedido.estado), 0)
    return render(request, 'store/tracking.html', {
        'pedido': pedido,
        'estados': estados,
        'current_index': current_index
    })

# Función para avanzar el estado del pedido automáticamente
def advance_order_status(pedido):
    estados = [estado[0] for estado in PEDIDO_ESTADOS]
    current_index = estados.index(pedido.estado) if pedido.estado in estados else 0
    
    if current_index < len(estados) - 1 and pedido.estado != 'entregado' and pedido.estado != 'cancelado':
        # Calcular tiempo transcurrido desde la creación del pedido
        tiempo_transcurrido = datetime.now(pedido.created_at.tzinfo) - pedido.created_at
        segundos_transcurridos = tiempo_transcurrido.total_seconds()
        
        # Avanzar estado cada 30 segundos (30s, 60s, 90s, 120s, 150s)
        # Cada 30 segundos avanza un estado
        estado_objetivo = min(int(segundos_transcurridos / 30), len(estados) - 1)
        
        if estado_objetivo > current_index:
            # Avanzar al siguiente estado
            next_index = current_index + 1
            if next_index < len(estados):
                pedido.estado = estados[next_index]
                pedido.save()
                send_tracking_email(pedido)

def send_tracking_email(pedido):
    try:
        subject = f'Actualización de tu pedido #{pedido.numero_pedido} - ScrewFX'
        message = f'''
        Hola {pedido.user.username},
        
        Tu pedido #{pedido.numero_pedido} ha sido actualizado.
        
        Estado actual: {pedido.get_estado_display()}
        Total: ${pedido.total}
        
        Puedes hacer seguimiento de tu pedido en: http://localhost:8000/tracking/{pedido.id}/
        
        Gracias por tu compra,
        Equipo ScrewFX
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@screwfx.com',
            [pedido.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f'Error enviando email de tracking: {e}')

# Vista para actualizar estado del pedido (AJAX)
@login_required
def update_tracking(request, pedido_id):
    if request.method == 'GET':
        pedido = get_object_or_404(Pedido, pk=pedido_id, user=request.user)
        # Avanzar estado si es necesario
        advance_order_status(pedido)
        pedido.refresh_from_db()
        return JsonResponse({
            'estado': pedido.estado,
            'estado_display': pedido.get_estado_display(),
            'numero_pedido': pedido.numero_pedido
        })

# Vista para listar pedidos del usuario
@login_required
def my_orders(request):
    pedidos = Pedido.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'pedidos': pedidos})