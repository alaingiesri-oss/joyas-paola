# 📖 Manual Maestro de Mantenimiento - Joyas Paola España Ribera

Este documento contiene toda la información técnica, preferencias, conexiones y pasos detallados para mantener, probar y actualizar tu aplicación de catálogo digital. Consérvalo en tu proyecto para que cualquier futuro asistente de IA o tú misma puedan entender el sistema al instante.

---

## 🛠️ Arquitectura del Sistema

La aplicación está diseñada con dos ambientes separados para evitar errores o pérdida de datos:

1. **Ambiente Local (Pruebas)**:
   - Funciona en tu computadora ejecutando el archivo **`iniciar_local.bat`**.
   - Utiliza una base de datos local y aislada llamada `inventory.db` (SQLite).
   - **Ventaja**: Puedes registrar joyas de prueba, borrarlas, cambiar precios y experimentar todo lo que quieras de forma segura sin afectar lo que ven tus clientes en internet.

2. **Ambiente Web (Producción)**:
   - Es la página web que ven tus clientes en internet (`alaingiesri-oss-joyas-paola-app.streamlit.app`).
   - Se alimenta directamente de tu repositorio de **GitHub** (`alaingiesri-oss/joyas-paola`).
   - Se conecta de forma segura a tu base de datos permanente en la nube en **Neon.tech** usando la clave secreta `DATABASE_URL`.
   - **Ventaja**: Los datos de tus clientes, joyas y fotos están a salvo en la nube y nunca se borrarán al reiniciar la página.

---

## 🔑 Credenciales y Configuración de Base de Datos

### Conexión a Neon.tech (PostgreSQL)
Tu base de datos permanente en internet está configurada con los siguientes parámetros:
* **Proveedor**: Neon.tech
* **Cuenta de acceso**: `paholy93@hotmail.com` (Iniciando sesión con esta cuenta en [console.neon.tech](https://console.neon.tech/))
* **Nombre del Proyecto**: `joyas-paola`
* **Enlace de Conexión (DATABASE_URL)**:
  `postgresql://neondb_owner:npg_hfwapZ3G7tSW@ep-fancy-hall-aq2tvk2p-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

### Configuración en Streamlit Cloud
Este enlace de conexión está guardado de forma segura en los **Secrets** de tu aplicación en Streamlit Cloud.
* **Clave en secretos**: `DATABASE_URL`

---

## 🚀 Pasos para Probar y Actualizar (Flujo de Trabajo)

Cuando quieras hacer cambios o probar cosas nuevos, sigue estrictamente este orden:

### Paso 1: Probar en tu computadora (Local)
1. Haz doble clic en **`iniciar_local.bat`** en la carpeta del proyecto.
2. Se abrirá una pantalla negra de comandos y luego tu navegador de internet en la dirección `http://localhost:8501`.
3. Prueba todas las funciones (añadir al carrito, CRUD de joyas, configuración, etc.).
4. Si todo funciona perfectamente, cierra la ventana negra para detener la prueba.

### Paso 2: Subir la actualización a GitHub (Internet)
Una vez que verificaste que todo está bien en local, súbelo a internet:
1. Abre tu navegador y ve a: **[Subir archivos en GitHub](https://github.com/alaingiesri-oss/joyas-paola/upload/principal)**
2. Arrastra y suelta los archivos que modificaste (por ejemplo, `app.py`, `database.py` o `README.md`).
3. Haz clic en el botón verde **Commit changes** (Confirmar cambios).
4. Streamlit leerá los cambios y actualizará la página web pública automáticamente en 1 minuto.

---

## ⚙️ Parámetros Autogestionables en la Web (Admin)

El catálogo web tiene un panel de administración protegido.
* **Contraseña por defecto**: `papavi` (Se ingresa en la barra lateral izquierda).
* **Gestión de Configuración**: Una vez ingresas la clave, puedes cambiar los siguientes valores desde la pestaña **Configuración de Tienda**:
  - **Número de WhatsApp**: Celular al que llegan los pedidos (con código de país, ej: `59172825322`).
  - **Contraseña**: Cambiar la clave `papavi` por una personalizada.
  - **Categorías**: Texto separado por comas con las categorías que desees mostrar (se actualiza en toda la app de inmediato).
  - **Materiales**: Texto separado por comas con los materiales de las joyas (se actualiza de inmediato).
  - **QR de Pago**: Imagen del código QR bancario para cobrar.
