# Joyas Paola España Ribera - Catálogo Digital

Aplicación interactiva y autogestionable desarrollada en Python (Streamlit) para administrar un inventario de joyas y generar catálogos en formato PDF profesionales y elegantes.

## Características

- **Catálogo Público y Carrito**: Los clientes pueden navegar por la galería interactiva, filtrar piezas por categorías/materiales y añadir productos directamente a su carrito de compras con ajuste dinámico de cantidades.
- **Checkout con Integración de WhatsApp y Geolocalización**: El comprador ingresa sus datos, obtiene opcionalmente sus coordenadas GPS con un clic, visualiza el código QR de pago del negocio y genera automáticamente un pedido pre-formateado para enviarse por WhatsApp al número de la joyería.
- **Área Administrativa Segura**: Panel administrativo oculto y protegido por contraseña para registrar nuevas piezas, gestionar el inventario de joyas y configurar la tienda.
- **Configuración de Tienda Autogestionable**: Permite al administrador cargar su propio código QR de pago, actualizar su número de WhatsApp receptor y cambiar la contraseña de acceso directamente desde la interfaz web.
- **Generación de Catálogos PDF**: Permite descargar un PDF profesional en 2 columnas con portada personalizada y datos de contacto de **Paola España Ribera**.
- **Base de Datos Robusta**: Funciona en la nube con PostgreSQL y utiliza almacenamiento Base64 para máxima portabilidad de imágenes.

## Despliegue en la Nube

Para subir gratis a internet y usar desde el celular:

1. Crea una base de datos PostgreSQL gratuita en [Neon.tech](https://neon.tech).
2. Sube los archivos `app.py`, `database.py`, `pdf_generator.py` y `requirements.txt` a un repositorio en GitHub.
3. Conéctalo a [Streamlit Community Cloud](https://share.streamlit.io).
4. En **Advanced Settings**, añade tu secreto:
   ```toml
   DATABASE_URL = "tu_cadena_de_conexion_de_neon_aqui"
   ```
