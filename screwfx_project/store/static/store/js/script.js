document.addEventListener('DOMContentLoaded', () => {
    console.log('Script loaded');

    // Lógica de login
    const loginForm = document.getElementById('loginForm');
    const logoutBtn = document.getElementById('logoutBtn');
    const errorMsg = document.getElementById('error');

    if (loginForm) {
        console.log('Login form found');
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();

            if (username.length < 6 || password.length < 6) {
                errorMsg.textContent = '⚠️ El usuario y la contraseña deben tener al menos 6 caracteres.';
                return;
            }

            fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/';
                } else {
                    errorMsg.textContent = '⚠️ Usuario o contraseña incorrectos.';
                }
            })
            .catch(error => {
                errorMsg.textContent = '⚠️ Error al iniciar sesión.';
                console.error('Error:', error);
            });
        });
    } else {
        console.log('Login form not found');
    }

    if (logoutBtn) {
        console.log('Logout button found');
        logoutBtn.addEventListener('click', () => {
            fetch('/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/';
                }
            })
            .catch(error => console.error('Error:', error));
        });
    } else {
        console.log('Logout button not found');
    }

    // Lógica del carrito
    const cartIcon = document.querySelector('.cart-icon');
    const cartPanel = document.querySelector('.cart-panel');
    const cartOverlay = document.querySelector('.cart-overlay');
    const closeCart = document.querySelector('.close-cart');
    const addToCartButtons = document.querySelectorAll('.add-to-cart');

    console.log('Cart icon:', cartIcon);
    console.log('Cart panel:', cartPanel);
    console.log('Cart overlay:', cartOverlay);
    console.log('Close cart:', closeCart);
    console.log('Add to cart buttons:', addToCartButtons.length);

    if (!cartIcon || !cartPanel || !cartOverlay || !closeCart) {
        console.error('Uno o más elementos del carrito no se encontraron');
        return;
    }

    // Mostrar/Ocultar carrito
    cartIcon.addEventListener('click', () => {
        console.log('Cart icon clicked');
        cartPanel.classList.add('active');
        cartOverlay.style.display = 'block';
        cartPanel.style.display = 'block'; // Asegurar visibilidad
    });

    closeCart.addEventListener('click', () => {
        console.log('Close cart clicked');
        cartPanel.classList.remove('active');
        cartOverlay.style.display = 'none';
    });

    cartOverlay.addEventListener('click', () => {
        console.log('Overlay clicked');
        cartPanel.classList.remove('active');
        cartOverlay.style.display = 'none';
    });

 document.addEventListener('click', (e) => {
    if (e.target.classList.contains('add-to-cart')) {
        console.log('Add to cart clicked on:', e.target);
        const product = e.target.parentElement;
        const productName = product.querySelector('p').textContent;
        const productPrice = product.querySelector('p:nth-child(4)').textContent;
        const cartItems = document.querySelector('.cart-items');
        
        const item = document.createElement('div');
        item.textContent = `${productName} - ${productPrice}`;
        cartItems.appendChild(item);

        alert(`${productName} añadido al carrito!`);
    }
});

// Función para obtener el token CSRF desde las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Auto-ocultar mensajes después de 5 segundos
(function() {
    // Set para rastrear mensajes que ya están siendo procesados
    const processedMessages = new WeakSet();
    
    function autoHideMessages() {
        // Buscar todos los mensajes posibles
        const allMessages = document.querySelectorAll('.messages p, p.error, p.success, .error, .success');
        
        allMessages.forEach((message) => {
            // Evitar procesar el mismo mensaje múltiples veces
            if (processedMessages.has(message)) {
                return;
            }
            
            // Marcar como procesado
            processedMessages.add(message);
            
            // Asegurar que el mensaje tenga opacidad inicial y transición
            message.style.opacity = '1';
            message.style.transform = 'translateX(0)';
            message.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            
            // Ocultar después de 5 segundos
            const timeoutId = setTimeout(() => {
                if (message.parentNode) { // Verificar que aún existe en el DOM
                    message.style.opacity = '0';
                    message.style.transform = 'translateX(100px)';
                    
                    // Remover del DOM después de la animación
                    setTimeout(() => {
                        if (message.parentNode) {
                            const container = message.closest('.messages');
                            message.remove();
                            
                            // Si el contenedor .messages está vacío, ocultarlo también
                            if (container && container.querySelectorAll('p').length === 0) {
                                container.style.display = 'none';
                            }
                        }
                    }, 500);
                }
            }, 5000);
            
            // Guardar el timeout ID en el elemento para poder cancelarlo si es necesario
            message.dataset.hideTimeout = timeoutId;
        });
    }
    
    // Ejecutar cuando el DOM esté listo
    function initAutoHideMessages() {
        autoHideMessages();
        // Ejecutar nuevamente después de un pequeño delay para capturar mensajes que se carguen después
        setTimeout(autoHideMessages, 200);
        // También ejecutar después de 1 segundo por si acaso
        setTimeout(autoHideMessages, 1000);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAutoHideMessages);
    } else {
        initAutoHideMessages();
    }
    
    // También ejecutar cuando la página esté completamente cargada
    window.addEventListener('load', autoHideMessages);
})();