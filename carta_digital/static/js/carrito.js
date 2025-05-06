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



    window.addEventListener('load', function () {
        // Una vez cargada la página, mostrar el botón de entrada
        const enterButton = document.getElementById('enterButton');

        // Mostrar el botón cambiando display
        enterButton.style.display = 'inline-block';  // Lo mostramos después de la carga

        enterButton.addEventListener('click', function () {
            const preloader = document.getElementById('preloader');
            preloader.style.opacity = '0';  // Hacemos que se desvanezca
            setTimeout(() => {
                preloader.style.display = 'none';  // Ocultamos el preloader
            }, 500);
        });
    });

    

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
        if (!carritoLista || !carritoTotal || !btnVaciar) return; // Asegurarse de que btnVaciar exista

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

        // Mostrar u ocultar botón "Vaciar carrito"
        if (btnVaciar) {
            btnVaciar.style.display = carrito.length > 0 ? 'block' : 'none';
        }
    }

   
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
    // VALIDACIÓN DE MONTO ABONADO
    // ===============================

    const inputDineroAbona = document.getElementById('dineroAbona');
    const errorDineroAbona = document.getElementById('errorDineroAbona');

    // Función para obtener el total como número
    function obtenerTotalNumerico() {
        const totalTexto = document.getElementById('totalPedidoModal').value;
        return parseFloat(totalTexto.replace('$', '').replace(',', '.')) || 0;
    }

    // Mostrar feedback en tiempo real al escribir
    inputDineroAbona.addEventListener('input', () => {
        const monto = parseFloat(inputDineroAbona.value);
        const total = obtenerTotalNumerico();

        // Verificación en tiempo real del monto
        if (!isNaN(monto) && monto >= total) {
            inputDineroAbona.classList.remove('is-invalid');
            inputDineroAbona.classList.add('is-valid');
            errorDineroAbona.style.display = 'none'; // Ocultar mensaje de error
        } else {
            inputDineroAbona.classList.remove('is-valid');
            inputDineroAbona.classList.add('is-invalid');
            errorDineroAbona.style.display = 'block';
            errorDineroAbona.textContent = 'El monto ingresado debe ser mayor o igual al total del pedido.';
        }
    });

    document.getElementById('pedidoForm').addEventListener('submit', function (e) {
        const monto = parseFloat(document.getElementById('dineroAbona').value);
        const total = parseFloat(document.getElementById('totalPedidoModal').value.replace('$', '').replace(',', '')); // Asumiendo que 'totalPedidoModal' contiene el monto en formato "$0.00"

        // Verifica si el monto es válido y si es menor que el total
        if (isNaN(monto) || monto < total) {
            e.preventDefault(); // Previene el envío del formulario
            document.getElementById('dineroAbona').classList.remove('is-valid');
            document.getElementById('dineroAbona').classList.add('is-invalid');
            document.getElementById('errorDineroAbona').style.display = 'block';
            document.getElementById('errorDineroAbona').textContent = 'El monto ingresado debe ser mayor o igual al total del pedido.';
            document.getElementById('dineroAbona').focus(); // Enfoca el campo para mejorar la UX
            return false; // Asegura que no se envíe el formulario
        }
    });


    document.addEventListener('DOMContentLoaded', function () {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(t => new bootstrap.Tooltip(t));
    });

   // ===============================
    // MOSTRAR/OCULTAR CARRITO EN MÓVILES (REVISADO)
    // ===============================

    const carritoIcono = document.querySelector('.floating-cart-icon');
    const carritoDropdown = document.querySelector('.cart-dropdown');
    const esMovil = window.matchMedia('(max-width: 991.98px)');
    let carritoVisible = false;

    function mostrarCarrito() {
        if (carritoDropdown) {
            carritoDropdown.classList.add('mostrar');
            carritoVisible = true;
        }
    }

    function ocultarCarrito() {
        if (carritoDropdown) {
            carritoDropdown.classList.remove('mostrar');
            carritoVisible = false;
        }
    }

    if (carritoIcono && carritoDropdown) {
        carritoIcono.addEventListener('click', function (event) {
            if (esMovil.matches) {
                event.preventDefault(); // Prevenir el comportamiento predeterminado del clic en móviles
                if (carritoVisible) {
                    ocultarCarrito();
                } else {
                    mostrarCarrito();
                }
            }
        });

        document.addEventListener('click', function (event) {
            if (esMovil.matches && carritoVisible && !carritoDropdown.contains(event.target) && event.target !== carritoIcono) {
                ocultarCarrito();
            }
        });

        carritoDropdown.addEventListener('click', function (event) {
            if (esMovil.matches) {
                event.stopPropagation(); // Detener la propagación dentro del dropdown en móviles
            }
        });
    }


    // Script para mostrar/ocultar el campo de detalles si selecciona "Otro"
    document.getElementById('tipoProyecto').addEventListener('change', function () {
        var tipoProyecto = this.value;
        var detallesDiv = document.getElementById('detallesTipoProyecto');

        if (tipoProyecto === 'Otro') {
            detallesDiv.style.display = 'block';
        } else {
            detallesDiv.style.display = 'none';
        }
    });

    // Modificar la URL de WhatsApp con los datos del formulario
    document.getElementById('formProyecto').addEventListener('submit', function (event) {
        event.preventDefault();

        var tipoProyecto = document.getElementById('tipoProyecto').value;
        var descripcion = document.getElementById('descripcion').value;
        var tiempoEntrega = document.getElementById('tiempoEntrega').value;
        var presupuesto = document.getElementById('presupuesto').value;
        var informacionAdicional = document.getElementById('informacionAdicional').value;
        var nombre = document.getElementById('nombre').value;
        var email = document.getElementById('email').value;
        var telefono = document.getElementById('telefono').value;

        // Crear el mensaje de WhatsApp
        var mensaje = `*Formulario de Proyecto solicitado(capriccio)*\n\n` +
            `*Tipo de Proyecto:* ${tipoProyecto}\n` +
            `*Descripción del Proyecto:* ${descripcion}\n` +
            `*Tiempo Estimado de Entrega:* ${tiempoEntrega}\n` +
            `*Presupuesto Estimado:* $${presupuesto}\n` +
            `*Información Adicional:* ${informacionAdicional}\n` +
            `\n*Datos de Contacto*\n` +
            `*Nombre:* ${nombre}\n` +
            `*Correo Electrónico:* ${email}\n` +
            `*Teléfono:* ${telefono}`;

        // Reemplaza este número por tu número de WhatsApp
        var numeroWhatsApp = '5491126884940'; // Tu número de WhatsApp aquí

        // Redirigir a WhatsApp con el mensaje
        var url = `https://wa.me/${numeroWhatsApp}?text=${encodeURIComponent(mensaje)}`;
        window.open(url, '_blank');
    });


    




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