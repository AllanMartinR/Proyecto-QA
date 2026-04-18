document.addEventListener('DOMContentLoaded', () => {
    console.log('Cart script loaded');
    const cartIcon = document.querySelector('.cart-icon');
    const cartPanel = document.querySelector('.cart-panel');
    const cartOverlay = document.querySelector('.cart-overlay');
    const closeCart = document.querySelector('.close-cart');

    if (!cartIcon || !cartPanel || !cartOverlay || !closeCart) {
        console.error('Elementos del carrito no encontrados');
        return;
    }

    cartIcon.addEventListener('click', () => {
        console.log('Cart opened');
        cartPanel.classList.add('active');
        cartOverlay.style.display = 'block';
    });

    closeCart.addEventListener('click', () => {
        console.log('Cart closed');
        cartPanel.classList.remove('active');
        cartOverlay.style.display = 'none';
    });

    cartOverlay.addEventListener('click', () => {
        console.log('Overlay clicked');
        cartPanel.classList.remove('active');
        cartOverlay.style.display = 'none';
    });
});