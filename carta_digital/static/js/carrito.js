document.addEventListener("DOMContentLoaded", function () {

    // ============================
    // VARIABLES Y ELEMENTOS BASE
    // ============================

    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    const carritoLista = document.getElementById('cart-items');
    const carritoTotal = document.getElementById('total-price');
    const btnVaciar = document.getElementById('clear-cart-button');
    const navbarCount = document.getElementById('navbar-cart-count');
    const floatingCount = document.getElementById('floating-cart-count');
    const btnFinalizarPedido = document.getElementById('btnFinalizarPedido');
    const aliasBox = document.getElementById('aliasMercadoPago');
    const mensajeEfectivo = document.getElementById('mensajeEfectivo');
    const dineroAbonaDiv = document.getElementById('dineroAbonaDiv'); // Nuevo
    const dineroAbonaInput = document.getElementById('dineroAbona'); // Nuevo
    const totalPedidoModalInput = document.getElementById('totalPedidoModal'); // Asegúrate de tener esta línea

    // Elementos para cambio de tema
    // const themeToggleCheckbox = document.getElementById('theme-toggle');
    // const themeToggleIcon = document.getElementById('theme-toggle-icon');
    // const lightStyle = document.getElementById('light-style');
    // const darkStyle = document.getElementById('dark-style');

    // ============================
    // FUNCIONES DE UI Y CARRITO
    // ============================

    // Actualiza los contadores del carrito en el navbar y carrito flotante
    function actualizarContador() {
        const cantidadTotal = carrito.reduce((acc, item) => acc + item.cantidad, 0);
        [navbarCount, floatingCount].forEach(el => {
            if (!el) return;
            el.textContent = cantidadTotal;

            if (cantidadTotal > 0) {
                el.classList.add('has-items');
                el.classList.remove('bounce');
                void el.offsetWidth; // fuerza reflow
                el.classList.add('bounce');
            } else {
                el.classList.remove('has-items', 'bounce');
            }
        });
    }

    // Animación para feedback visual del contador
    function animarContador(tipo = 'bounce') {
        [navbarCount, floatingCount].forEach(el => {
            if (!el) return;
            el.classList.remove(tipo);
            void el.offsetWidth;
            el.classList.add(tipo);
        });
    }

    // Muestra el carrito en pantalla
    function renderizarCarrito() {
        if (!carritoLista || !carritoTotal) return;

        carritoLista.innerHTML = '';
        let total = 0;

        carrito.forEach(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;

            const li = document.createElement('li');
            li.innerHTML = `
                <div class="cart-item-details">
                    <span class="cart-item-name">${item.nombre}</span>
                    <div class="quantity-controls">
                        <button class="btn btn-sm btn-outline-secondary disminuir-cantidad" data-id="${item.id}">−</button>
                        <span class="cart-item-qty">${item.cantidad}</span>
                        <button class="btn btn-sm btn-outline-secondary aumentar-cantidad" data-id="${item.id}">+</button>
                    </div>
                    <span class="cart-item-price">$${subtotal.toFixed(2)}</span>
                </div>
                <button class="btn btn-sm eliminar-item text-danger" data-id="${item.id}">×</button>
            `;
            li.classList.add('d-flex', 'justify-content-between', 'align-items-center', 'mb-2');
            carritoLista.appendChild(li);
        });

        carritoTotal.textContent = total.toFixed(2);
        if (totalPedidoModalInput) {
            totalPedidoModalInput.value = `$${total.toFixed(2)}`;
        }

        actualizarContador();
        localStorage.setItem('carrito', JSON.stringify(carrito));

        // Mostrar u ocultar botón "Finalizar pedido"
        if (btnFinalizarPedido) {
            btnFinalizarPedido.style.display = carrito.length > 0 ? 'block' : 'none';
        }
    }

    // ===============================
    // MANEJO DEL TEMA CLARO/OSCURO
    // ===============================

    // Aplica el tema guardado en localStorage
    // if (localStorage.getItem('darkMode') === 'true') {
    //   darkStyle.disabled = false;
    // themeToggleCheckbox.checked = true;
    //   document.body.classList.add('dark-mode');
    //   themeToggleIcon.classList.replace('bi-moon-fill', 'bi-sun-fill');
    // }

    // Actualiza el icono del botón de tema
    // function updateThemeIcon() {
    //     if (themeToggleCheckbox.checked) {
    //         themeToggleIcon.classList.replace('bi-moon-fill', 'bi-sun-fill');
    //     } else {
    //        themeToggleIcon.classList.replace('bi-sun-fill', 'bi-moon-fill');
    //     }
    // }

    // Cambia el tema al hacer clic en el toggle
    // if (themeToggleCheckbox) {
    //    themeToggleCheckbox.addEventListener('change', () => {
    //        const dark = themeToggleCheckbox.checked;
    //        darkStyle.disabled = !dark;
    //        lightStyle.disabled = dark;
    //       document.body.classList.toggle('dark-mode', dark);
    //       localStorage.setItem('darkMode', dark);
    //      updateThemeIcon();
    //   });
    // }

    // ===============================
    // INICIALIZA CARRITO EN PANTALLA
    // ===============================
    renderizarCarrito();

    // ===============================
    // AGREGAR PRODUCTO AL CARRITO
    // ===============================

    const botonesAgregar = document.querySelectorAll('.agregar-carrito');
    if (botonesAgregar) {
        botonesAgregar.forEach(boton => {
            boton.addEventListener('click', () => {
                const { id, nombre, precio, imagen } = boton.dataset;
                const existente = carrito.find(p => p.id === id);
                if (existente) {
                    existente.cantidad += 1;
                } else {
                    carrito.push({ id, nombre, precio: parseFloat(precio), imagen, cantidad: 1 });
                }
                animarContador();
                renderizarCarrito();
            });
        });
    }

    // ===============================
    // MODIFICAR CANTIDAD O ELIMINAR
    // ===============================

    if (carritoLista) {
        carritoLista.addEventListener('click', (e) => {
            const id = e.target.dataset.id;
            const item = carrito.find(p => p.id === id);

            if (e.target.classList.contains('aumentar-cantidad') && item) {
                item.cantidad += 1;
                renderizarCarrito();
            }

            if (e.target.classList.contains('disminuir-cantidad')) {
                if (item && item.cantidad > 1) {
                    item.cantidad -= 1;
                } else {
                    const index = carrito.findIndex(p => p.id === id);
                    if (index !== -1) carrito.splice(index, 1);
                }
                renderizarCarrito();
            }

            if (e.target.classList.contains('eliminar-item')) {
                const index = carrito.findIndex(p => p.id === id);
                if (index !== -1) {
                    const li = e.target.closest('li');
                    li.classList.add('slide-out');
                    li.addEventListener('animationend', () => {
                        carrito.splice(index, 1);
                        renderizarCarrito();
                        animarContador('shake');
                    });
                }
            }
        });
    }

    // ===============================
    // VACIAR TODO EL CARRITO
    // ===============================

    if (btnVaciar) {
        btnVaciar.addEventListener('click', () => {
            carrito.length = 0;
            renderizarCarrito();
            if (aliasBox) aliasBox.style.display = 'none';
            if (mensajeEfectivo) mensajeEfectivo.style.display = 'none';
            if (dineroAbonaDiv) dineroAbonaDiv.style.display = 'none';
        });
    }

    // ===============================
    // ENVÍO DE PEDIDO POR WHATSAPP
    // ===============================

    const pedidoForm = document.getElementById('pedidoForm');
    if (pedidoForm) {
        pedidoForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const nombre = document.getElementById('nombreCliente').value.trim();
            const direccion = document.getElementById('direccionCliente').value.trim();
            const entreCalles = document.getElementById('entreCalles').value.trim();
            const modoCompra = document.querySelector('input[name="modoCompra"]:checked')?.value;
            const metodoPago = document.querySelector('input[name="metodoPago"]:checked')?.value;
            const comentarios = document.getElementById('comentarios').value.trim();
            const dineroAbona = dineroAbonaInput?.value.trim(); // Get the value if the element exists

            if (!nombre || !direccion || !entreCalles || !modoCompra || !metodoPago) {
                alert('Por favor completá todos los campos obligatorios.');
                return;
            }

            if (metodoPago === 'efectivo' && !dineroAbona) {
                alert('Por favor, indica con cuánto dinero abona el cliente.');
                return;
            }

            if (carrito.length === 0) {
                alert('Tu carrito está vacío.');
                return;
            }

            let detalle = '';
            carrito.forEach(item => {
                detalle += `• ${item.nombre} x${item.cantidad} - $${(item.precio * item.cantidad).toFixed(2)}\n`;
            });

            const total = carrito.reduce((acc, item) => acc + item.precio * item.cantidad, 0);

            let mensaje = `*📦 Nuevo Pedido desde la App*\n\n`;
            mensaje += `👤 *Nombre:* ${nombre}\n`;
            mensaje += `🏠 *Dirección:* ${direccion}\n`;
            mensaje += `📍 *Entre calles:* ${entreCalles}\n`;
            mensaje += `🛍️ *Modo de compra:* ${modoCompra}\n`;
            mensaje += `💳 *Método de pago:* ${metodoPago}\n`;
            if (metodoPago === 'efectivo' && dineroAbona) {
                mensaje += `💰 *Abona con:* $${dineroAbona}\n`;
            }
            mensaje += `💰 *Total:* $${total.toFixed(2)}\n\n`;
            mensaje += `\n🧾 *Detalle del pedido:*\n${detalle}`;
            if (comentarios) mensaje += `📝 *Comentarios:* ${comentarios}\n`;
            mensaje += `\n✅ Pedido generado desde la carta digital.`;

            const telefono = '5491126884940'; // Reemplaza con tu número de teléfono
            const url = `https://wa.me/${telefono}?text=${encodeURIComponent(mensaje)}`;

            localStorage.removeItem('carrito');
            carrito.length = 0;
            renderizarCarrito();
            if (aliasBox) aliasBox.style.display = 'none';
            if (mensajeEfectivo) mensajeEfectivo.style.display = 'none';
            if (dineroAbonaDiv) dineroAbonaDiv.style.display = 'none';

            window.open(url, '_blank');

            if (metodoPago === 'mercadopago') {
                const alias = 'pola7188'; // Reemplaza con tu alias de MercadoPago
                alert(`Recordá transferir a:\nAlias: ${alias}`);
                window.open(`https://www.mercadopago.com.ar/transfer?alias=${alias}`, '_blank');
            }
        });

        // Mostrar/ocultar información extra según el método de pago
        const radiosMetodoPago = document.querySelectorAll('input[name="metodoPago"]');
        radiosMetodoPago.forEach(radio => {
            radio.addEventListener('change', () => {
                const metodo = radio.value;

                if (aliasBox) {
                    aliasBox.style.display = metodo === 'mercadopago' ? 'block' : 'none';
                    if (metodo === 'mercadopago') aliasBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }

                if (mensajeEfectivo) {
                    mensajeEfectivo.style.display = metodo === 'efectivo' ? 'block' : 'none';
                    if (metodo === 'efectivo') mensajeEfectivo.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }

                if (dineroAbonaDiv) {
                    dineroAbonaDiv.style.display = metodo === 'efectivo' ? 'block' : 'none';
                    if (metodo === 'efectivo') {
                        dineroAbonaInput.required = true;
                        dineroAbonaDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    } else {
                        dineroAbonaInput.required = false;
                    }
                }
            });
        });
    }

    // ===============================
    // BUSCADOR DE PRODUCTOS CON SCROLL
    // ===============================

    const buscador = document.getElementById('buscador');
    const productos = document.querySelectorAll('.producto-item');
    const resultadosBusqueda = document.getElementById('resultados-busqueda');

    if (buscador && resultadosBusqueda) {
        buscador.addEventListener('input', function () {
            const valor = buscador.value.toLowerCase().trim();
            resultadosBusqueda.innerHTML = '';

            if (valor === '') {
                productos.forEach(producto => {
                    producto.classList.remove('oculto');
                    producto.style.display = '';
                });
                resultadosBusqueda.style.display = 'none';
                return;
            }

            const productosEncontrados = [];

            productos.forEach(producto => {
                const nombre = producto.dataset.nombre?.toLowerCase() || '';
                if (nombre.includes(valor)) {
                    productosEncontrados.push(producto.cloneNode(true));
                    producto.classList.remove('oculto');
                    producto.style.display = 'none';
                } else {
                    producto.classList.add('oculto');
                    producto.style.display = 'none';
                }
            });

            if (productosEncontrados.length > 0) {
                resultadosBusqueda.style.display = 'block';
                const resultadoTexto = document.createElement('p');
                resultadoTexto.innerHTML = `🔍 <strong>${productosEncontrados.length}</strong> producto(s) encontrado(s):`;
                resultadosBusqueda.appendChild(resultadoTexto);

                productosEncontrados.forEach(prod => {
                    const contenedor = document.createElement('div');
                    contenedor.classList.add('producto-scroll');
                    contenedor.appendChild(prod);
                    resultadosBusqueda.appendChild(contenedor);
                });

                resultadosBusqueda.scrollIntoView({ behavior: 'smooth', block: 'start' });

            } else {
                resultadosBusqueda.style.display = 'block';
                resultadosBusqueda.innerHTML = `<p>❌ No se encontraron coincidencias.</p>`;
            }
        });
    }

    // ===============================
    // FILTRO EN VIVO POR NOMBRE
    // ===============================

    const inputBuscador = document.getElementById('buscador-productos');
    if (inputBuscador) {
        inputBuscador.addEventListener('input', function () {
            const filtro = inputBuscador.value.toLowerCase();
            const tarjetas = document.querySelectorAll('#todos-los-productos .producto-item'); // Correctly targeting the name

            tarjetas.forEach(card => {
                const nombreProductoElement = card.querySelector('.producto-nombre'); // Correctly targeting the name
                const visible = nombreProductoElement && nombreProductoElement.textContent.toLowerCase().includes(filtro);
                card.style.display = visible ? 'block' : 'none';
            });
        });
    }


});