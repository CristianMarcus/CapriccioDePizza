🧠 Resumen del funcionamiento del script principal
🔄 1. Inicialización
Cuando se carga la página, se recupera el carrito desde localStorage.

Se configura el tema claro u oscuro guardado anteriormente.

Se renderiza el contenido del carrito y se actualizan los contadores en la interfaz.

🛒 2. Carrito de compras
Los productos se agregan al carrito al hacer clic en los botones .agregar-carrito.

Se actualiza el contador de productos en la navbar y botón flotante con animaciones.

Se muestra el listado de productos con su nombre y precio.

Se pueden eliminar productos uno por uno con un botón × (con animación de salida).

También se puede vaciar todo el carrito con el botón "Vaciar carrito".

El contenido se guarda automáticamente en localStorage.

🌗 3. Modo oscuro
El usuario puede alternar entre modo claro y oscuro desde un botón.

El tema se guarda en localStorage y se aplica automáticamente al recargar la página.

📦 4. Formulario de pedido
El usuario debe completar: nombre, dirección, entre calles, modo de compra, método de pago y comentarios opcionales.

El sistema valida que todos los campos estén completos y que haya productos en el carrito.

Se genera un mensaje de pedido detallado incluyendo:

Datos del cliente.

Lista de productos.

Total.

Comentarios.

Ese mensaje se envía a WhatsApp automáticamente al hacer clic en "Enviar pedido".

💳 5. Métodos de pago
Si elige MercadoPago:

Se muestra un alias (capricciopizzas.mp) en pantalla.

Se intenta abrir la app de MercadoPago con ese alias.

Si no se puede, se redirige al sitio web de MercadoPago como alternativa.

También se muestra un alert recordando al usuario el alias para hacer la transferencia.

🧼 6. Limpieza final
Una vez enviado el pedido, se vacía el carrito.

Se actualiza la interfaz para reflejar el carrito vacío.
