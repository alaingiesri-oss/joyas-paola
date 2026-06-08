import streamlit as st
import os
import uuid
import base64
import urllib.parse
from io import BytesIO
from PIL import Image as PILImage
import streamlit.components.v1 as components
import database
import pdf_generator

def encode_image_to_base64(uploaded_file):
    """Comprime la imagen cargada y la convierte en una cadena Base64."""
    if uploaded_file is None:
        return ""
    try:
        img = PILImage.open(uploaded_file)
        
        # Convertir a RGB si tiene transparencia (para guardar en JPEG comprimido)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = PILImage.new("RGB", img.size, (255, 255, 255))
            try:
                mask = img.split()[3]
            except IndexError:
                mask = None
            background.paste(img, mask=mask)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Redimensionar para optimizar almacenamiento en DB (máx 800x600)
        img.thumbnail((800, 600))
        
        # Comprimir a JPEG y codificar a Base64
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        return ""

def get_local_image_base64(file_path):
    """Convierte una imagen local en una cadena Base64."""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded_string}"
    except Exception:
        return None

# Configuración de página con título e ícono
st.set_page_config(
    page_title="Gestor de Joyas - Paola España Ribera",
    page_icon="💎",
    layout="wide"
)

# Inicializar Base de Datos
database.init_db()

# Inicializar estados de la aplicación
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = {}
if 'edit_item_id' not in st.session_state:
    st.session_state.edit_item_id = None



# Estilo de diseño premium (CSS personalizado)
st.markdown("""
    <style>
    /* Importar fuente elegante */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, .title-lux {
        font-family: 'Playfair Display', serif !important;
        font-weight: 700;
        color: #1A2B4C !important;
    }
    
    /* Botones primarios elegantes */
    div.stButton > button:first-child {
        background-color: #1A2B4C;
        color: #D4AF37;
        border: 1px solid #D4AF37;
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #D4AF37;
        color: #1A2B4C;
        border: 1px solid #1A2B4C;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(212, 175, 55, 0.25);
    }
    
    /* Estilos de pestañas de navegación personalizadas */
    button[kind="primary"] {
        background-color: #1A2B4C !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        border-bottom: 3px solid #D4AF37 !important;
        font-weight: bold !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 0.6rem 1rem !important;
        box-shadow: 0 4px 15px rgba(26, 43, 76, 0.15) !important;
    }
    
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #64748B !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    button[kind="secondary"]:hover {
        color: #1A2B4C !important;
        border-color: #D4AF37 !important;
        background-color: #F8FAFC !important;
    }
    
    /* Tarjetas de productos en la galería */
    .product-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        overflow: hidden;
    }
    
    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 30px rgba(212, 175, 55, 0.18);
        border-color: #D4AF37;
    }
    
    /* Efecto zoom de imagen elegante en las tarjetas */
    .product-card img {
        transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border-radius: 8px !important;
    }
    
    .product-card:hover img {
        transform: scale(1.06) !important;
    }
    
    /* Etiquetas de categoría y material */
    .badge-cat {
        background-color: #FFFFFF !important;
        color: #1A2B4C !important;
        padding: 5px 14px !important;
        border-radius: 50px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
        display: inline-block !important;
        border: 1px solid #D4AF37 !important;
        box-shadow: 0 2px 5px rgba(212,175,55,0.05) !important;
    }
    
    .badge-mat {
        background-color: #1A2B4C !important;
        color: #D4AF37 !important;
        padding: 5px 14px !important;
        border-radius: 50px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
        display: inline-block !important;
        border: 1px solid #D4AF37 !important;
        box-shadow: 0 2px 5px rgba(26,43,76,0.1) !important;
    }
    
    .price-text {
        font-size: 1.35rem;
        font-weight: 700;
        color: #27AE60;
        margin-top: 8px;
    }
    
    /* Sidebar premium */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Estilo del banner del título */
    .header-banner {
        background: linear-gradient(135deg, #1A2B4C 0%, #2A4365 100%);
        padding: 2.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #D4AF37;
    }
    
    .header-banner h1 {
        color: #D4AF37 !important;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .header-banner p {
        color: #E2E8F0;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Botón de WhatsApp verde */
    .whatsapp-btn {
        background-color: #25D366 !important;
        color: white !important;
        border: 1px solid #128C7E !important;
        border-radius: 4px;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        text-align: center;
        display: block;
        transition: all 0.3s ease;
        text-decoration: none;
    }
    .whatsapp-btn:hover {
        background-color: #128C7E !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.25);
    }
    
    /* Footer de lujo */
    .footer-lux {
        background: linear-gradient(135deg, #1A2B4C 0%, #0F172A 100%);
        color: #E2E8F0;
        padding: 2.5rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 4rem;
        border-top: 4px solid #D4AF37;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .footer-lux h4 {
        color: #D4AF37 !important;
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .footer-lux p {
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
        color: #CBD5E1;
    }
    </style>
""", unsafe_allow_html=True)

# --- LISTAS DE SELECCIÓN DINÁMICAS DESDE LA BASE DE DATOS ---
categories_setting = database.get_setting("categories", database.DEFAULT_CATEGORIES)
materials_setting = database.get_setting("materials", database.DEFAULT_MATERIALS)

CATEGORIES = [c.strip() for c in categories_setting.split(",") if c.strip()]
MATERIALS = [m.strip() for m in materials_setting.split(",") if m.strip()]


# --- ICONOS PARA CATEGORÍAS Y MATERIALES ---
CATEGORY_ICONS = {
    "anillo": "💍",
    "collar": "📿",
    "arete": "💎",
    "pulsera": "✨",
    "dije": "🌟",
    "cadena": "🔗",
    "gargantilla": "🎗️",
    "esclava": "💫",
    "baño de oro": "👑",
    "otro": "💎"
}

MATERIAL_ICONS = {
    "oro 18k": "🟡",
    "oro 24k": "🟡",
    "oro blanco": "⚪",
    "oro rosa": "🌸",
    "plata": "⚪",
    "platino": "💿",
    "acero": "🦾",
    "baño de oro": "👑",
    "pedrería": "✨"
}

def get_cat_with_icon(cat_name):
    c_clean = cat_name.strip()
    for key, icon in CATEGORY_ICONS.items():
        if key in c_clean.lower():
            return f"{icon} {c_clean}"
    return f"💎 {c_clean}"

def get_mat_with_icon(mat_name):
    m_clean = mat_name.strip()
    for key, icon in MATERIAL_ICONS.items():
        if key in m_clean.lower():
            return f"{icon} {m_clean}"
    return f"✨ {m_clean}"

# Banner de Encabezado Principal con Logo
logo_b64 = get_local_image_base64("logo.jpeg")
if logo_b64:
    st.markdown(f"""
        <div class="header-banner" style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1A2B4C 0%, #0F172A 100%); border: 1px solid #D4AF37; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
            <img src="{logo_b64}" style="max-height: 120px; margin-bottom: 10px; border-radius: 8px;">
            <p style="color: #D4AF37; font-size: 1.25rem; font-style: italic; margin-top: 0.5rem; font-family: 'Playfair Display', serif; letter-spacing: 1px; font-weight: 600;">"Brillo eterno y elegancia exclusiva en cada detalle"</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="header-banner">
            <h1>Joyas Paola España Ribera</h1>
            <p style="color: #D4AF37; font-size: 1.25rem; font-style: italic; font-family: 'Playfair Display', serif; font-weight: 600;">"Brillo eterno y elegancia exclusiva en cada detalle"</p>
        </div>
    """, unsafe_allow_html=True)

# --- LOGO PERMANENTE EN LA PARTE SUPERIOR DEL SIDEBAR ---
logo_path = "logo.jpeg"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
    st.sidebar.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

# --- PANEL DE ADMINISTRACIÓN EN SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Panel de Administración")


if not st.session_state.is_admin:
    admin_pwd_input = st.sidebar.text_input("Contraseña Administrador", type="password", key="admin_pwd_sidebar")
    if st.sidebar.button("Ingresar como Admin", key="admin_login_btn"):
        db_pwd = database.get_setting("admin_password", "papavi")
        if admin_pwd_input == db_pwd:
            st.session_state.is_admin = True
            st.sidebar.success("¡Sesión iniciada!")
            st.rerun()
        else:
            st.sidebar.error("Contraseña incorrecta")
else:
    st.sidebar.success("Sesión iniciada como Administrador")
    if st.sidebar.button("Cerrar Sesión", key="admin_logout_btn"):
        st.session_state.is_admin = False
        if 'checkout_data' in st.session_state:
            del st.session_state.checkout_data
        st.rerun()

# Definir pestañas según rol
if st.session_state.is_admin:
    tabs = [
        "🛍️ Catálogo y PDF", 
        "🛒 Mi Carrito",
        "➕ Agregar Nueva Joya", 
        "⚙️ Gestionar Inventario",
        "🔧 Configuración de Tienda"
    ]
else:
    tabs = [
        "🛍️ Catálogo Digital", 
        "🛒 Mi Carrito"
    ]

if 'active_tab' not in st.session_state or st.session_state.active_tab not in tabs:
    st.session_state.active_tab = tabs[0]

# Renderizar pestañas horizontales premium usando st.columns
cols = st.columns(len(tabs))
for idx, tab_name in enumerate(tabs):
    with cols[idx]:
        is_active = (st.session_state.active_tab == tab_name)
        button_type = "primary" if is_active else "secondary"
        if st.button(tab_name, key=f"nav_tab_{idx}", use_container_width=True, type=button_type):
            st.session_state.active_tab = tab_name
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- CONTENIDO: AGREGAR NUEVA JOYA ---
if st.session_state.is_admin and st.session_state.active_tab == "➕ Agregar Nueva Joya":
    if True:
        st.subheader("Agregar una nueva joya al inventario")
        
        with st.form("add_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nombre de la Joya*", placeholder="Ej. Anillo de Compromiso Diamante")
                price = st.number_input("Precio (Bs.)*", min_value=0.0, step=10.0, format="%.2f")
                description = st.text_area("Descripción detallada", placeholder="Ej. Anillo elaborado en oro blanco de 18 quilates con una esmeralda central...", height=120)
                
            with col2:
                st.write("Categoría (selecciona una o más)*")
                cat_cols = st.columns(3)
                selected_cats = []
                for i, cat in enumerate(CATEGORIES):
                    with cat_cols[i % 3]:
                        if st.checkbox(cat, key=f"cat_add_{cat}"):
                            selected_cats.append(cat)
                            
                st.write("Material (selecciona uno o más)*")
                mat_cols = st.columns(3)
                selected_mats = []
                for i, mat in enumerate(MATERIALS):
                    with mat_cols[i % 3]:
                        if st.checkbox(mat, key=f"mat_add_{mat}"):
                            selected_mats.append(mat)
                            
                uploaded_image = st.file_uploader("Fotografía de la joya", type=["jpg", "jpeg", "png"])
                
            submitted = st.form_submit_button("Registrar Joya")
            
            if submitted:
                if not name:
                    st.error("El nombre de la joya es requerido.")
                elif price <= 0:
                    st.error("El precio debe ser mayor a 0.")
                elif not selected_cats:
                    st.error("Debes seleccionar al menos una categoría.")
                elif not selected_mats:
                    st.error("Debes seleccionar al menos un material.")
                else:
                    image_path = ""
                    # Codificar imagen a Base64 si se sube una
                    if uploaded_image is not None:
                        image_path = encode_image_to_base64(uploaded_image)
                    
                    # Guardar en base de datos
                    categories_str = ", ".join(selected_cats)
                    materials_str = ", ".join(selected_mats)
                    
                    new_id = database.add_item(
                        name=name,
                        category=categories_str,
                        material=materials_str,
                        price=price,
                        description=description,
                        image_path=image_path
                    )
                    st.success(f"¡Joya '{name}' agregada exitosamente al inventario con ID {new_id}!")
                    st.rerun()

# --- CONTENIDO: CATÁLOGO Y GENERACIÓN DE PDF ---
if st.session_state.active_tab in ["🛍️ Catálogo Digital", "🛍️ Catálogo y PDF"]:
    # Sidebar de filtros y controles
    st.sidebar.header("Filtros del Catálogo")
    
    # Filtro de búsqueda por texto
    search_query = st.sidebar.text_input("Buscar por nombre", "")
    
    # Filtro de categoría (por casillas de verificación en el sidebar)
    st.sidebar.subheader("Categorías")
    filter_cats = []
    for cat in CATEGORIES:
        if st.sidebar.checkbox(cat, key=f"filter_cat_{cat}"):
            filter_cats.append(cat)
            
    # Filtro de material (por casillas de verificación en el sidebar)
    st.sidebar.subheader("Materiales")
    filter_mats = []
    for mat in MATERIALS:
        if st.sidebar.checkbox(mat, key=f"filter_mat_{mat}"):
            filter_mats.append(mat)
            
    # Configuración de generación de PDF
    st.sidebar.markdown("---")
    st.sidebar.header("Generación de Catálogo PDF")
    catalog_pdf_title = st.sidebar.text_input("Título del Catálogo", "Catálogo de Joyería Fina")

    
    # Obtener todas las joyas
    all_items = database.get_all_items()
    
    # Aplicar filtros
    filtered_items = []
    for item in all_items:
        # Búsqueda por nombre
        if search_query and search_query.lower() not in item['name'].lower():
            continue
            
        # Filtro de categorías (si se seleccionó alguna, la joya debe contener al menos una de las categorías seleccionadas)
        if filter_cats:
            item_cats = [c.strip() for c in (item['category'] or '').split(',')]
            if not any(fc in item_cats for fc in filter_cats):
                continue
                
        # Filtro de materiales (si se seleccionó alguno, la joya debe contener al menos uno de los materiales seleccionados)
        if filter_mats:
            item_mats = [m.strip() for m in (item['material'] or '').split(',')]
            if not any(fm in item_mats for fm in filter_mats):
                continue
                
        filtered_items.append(item)
        
    # Mostrar video promocional de la joyería si existe
    video_path = "procesalo.mp4"
    if os.path.exists(video_path):
        st.write("✨ **Conoce Nuestra Colección Exclusiva:**")
        st.video(video_path, autoplay=True, loop=True, muted=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
    st.subheader(f"Catálogo de Joyas ({len(filtered_items)} mostradas)")
    
    # Acciones masivas de selección para el catálogo
    if st.session_state.is_admin:
        col_sel1, col_sel2 = st.columns([1, 4])
        with col_sel1:
            if st.button("Seleccionar Todas"):
                for item in filtered_items:
                    st.session_state.selected_items[item['id']] = True
                st.rerun()
        with col_sel2:
            if st.button("Deseleccionar Todas"):
                for item in filtered_items:
                    st.session_state.selected_items[item['id']] = False
                st.rerun()

    # Generador de PDF en la barra lateral o en la sección superior
    if st.session_state.is_admin:
        items_to_include = [item for item in filtered_items if st.session_state.selected_items.get(item['id'], True)]
        st.sidebar.write(f"Joyas seleccionadas para el PDF: {len(items_to_include)}")
    else:
        items_to_include = filtered_items
    
    if len(items_to_include) > 0:
        pdf_btn = st.sidebar.button("Generar PDF")
        if pdf_btn:
            pdf_filename = "catalogo_joyas.pdf"
            try:
                logo_base64 = get_local_image_base64("logo.jpeg")
                pdf_generator.generate_catalog_pdf(
                    items_to_include, 
                    output_filename=pdf_filename, 
                    catalog_title=catalog_pdf_title,
                    logo_data=logo_base64
                )
                
                with open(pdf_filename, "rb") as f:
                    pdf_bytes = f.read()
                    
                st.sidebar.download_button(
                    label="⬇️ Descargar Catálogo PDF",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
                st.sidebar.success("¡Catálogo PDF generado con éxito!")
            except Exception as e:
                st.sidebar.error(f"Error generando PDF: {e}")
    else:
        st.sidebar.info("Selecciona al menos una joya para generar el PDF.")

    # Mostrar catálogo de joyas en cuadrícula en la UI
    if not filtered_items:
        st.info("No se encontraron joyas que coincidan con los filtros seleccionados.")
    else:
        # Mostramos en cuadrícula de 3 columnas
        cols = st.columns(3)
        for idx, item in enumerate(filtered_items):
            with cols[idx % 3]:
                # Inicializar estado de selección de la joya (por defecto seleccionada para catálogo)
                if item['id'] not in st.session_state.selected_items:
                    st.session_state.selected_items[item['id']] = True
                    
                # Caja contenedora
                st.markdown(f"""
                    <div class="product-card">
                        <h3 style="margin-top:0; margin-bottom:5px; font-size:1.3rem;">{item['name']}</h3>
                        <p style="margin-bottom:10px;"><span class="price-text">Bs. {item['price']:,.2f}</span></p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Mostrar imagen en Streamlit (soporta Base64 y rutas locales)
                has_image = False
                if item['image_path']:
                    if item['image_path'].startswith("data:image"):
                        st.image(item['image_path'], use_container_width=True)
                        has_image = True
                    elif os.path.exists(item['image_path']):
                        st.image(item['image_path'], use_container_width=True)
                        has_image = True
                        
                if not has_image:
                    st.markdown("""
                        <div style="background-color:#F1F5F9; height:180px; display:flex; align-items:center; justify-content:center; border-radius:6px; border:1px dashed #CBD5E1; margin-bottom:10px;">
                            <span style="color:#64748B; font-style:italic;">Imagen no disponible</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Metadatos en formato badges
                cats = [c.strip() for c in (item['category'] or '').split(',')]
                mats = [m.strip() for m in (item['material'] or '').split(',')]
                
                badges_cat_html = "".join([f'<span class="badge-cat">{get_cat_with_icon(c)}</span>' for c in cats if c])
                badges_mat_html = "".join([f'<span class="badge-mat">{get_mat_with_icon(m)}</span>' for m in mats if m])
                
                st.markdown(f"<div>{badges_cat_html}{badges_mat_html}</div>", unsafe_allow_html=True)
                
                if item['description']:
                    st.markdown(f"<p style='color:#475569; font-size:0.9rem; margin-top:8px;'>{item['description']}</p>", unsafe_allow_html=True)
                
                # Checkbox para incluir en el catálogo PDF (solo Administradores)
                if st.session_state.is_admin:
                    st.session_state.selected_items[item['id']] = st.checkbox(
                        "Incluir en catálogo PDF", 
                        value=st.session_state.selected_items.get(item['id'], True), 
                        key=f"check_include_{item['id']}"
                    )
                
                # Controles del Carrito de Compras
                item_id = item['id']
                in_cart = item_id in st.session_state.cart
                if in_cart:
                    col_q1, col_q2, col_q3 = st.columns([1, 1, 1])
                    with col_q1:
                        if st.button("➖", key=f"minus_cart_{item_id}"):
                            if st.session_state.cart[item_id] > 1:
                                st.session_state.cart[item_id] -= 1
                            else:
                                del st.session_state.cart[item_id]
                            st.rerun()
                    with col_q2:
                        st.markdown(f"<div style='text-align:center; font-weight:bold; margin-top:6px; font-size:1.1rem;'>{st.session_state.cart[item_id]}</div>", unsafe_allow_html=True)
                    with col_q3:
                        if st.button("➕", key=f"plus_cart_{item_id}"):
                            st.session_state.cart[item_id] += 1
                            st.rerun()
                    
                    # Botón para ir al carrito
                    if st.button("🛒 Ver mi Carrito", key=f"go_to_cart_btn_{item_id}", use_container_width=True):
                        st.session_state.active_tab = "🛒 Mi Carrito"
                        st.rerun()
                else:
                    if st.button("🛒 Añadir al Carrito", key=f"add_cart_{item_id}", use_container_width=True):
                        st.session_state.cart[item_id] = 1
                        st.rerun()
                st.write("")

# --- CONTENIDO: GESTIONAR INVENTARIO (TABLA Y EDICIÓN/ELIMINACIÓN) ---
if st.session_state.is_admin and st.session_state.active_tab == "⚙️ Gestionar Inventario":
    if True:
        st.subheader("Administrar Joyas Registradas")
        
        # Obtener todos los productos
        all_items = database.get_all_items()
        
        if not all_items:
            st.info("No hay joyas en el inventario.")
        else:
            # Formulario de Edición (Si hay un ID seleccionado para editar)
            if st.session_state.edit_item_id is not None:
                item_to_edit = database.get_item(st.session_state.edit_item_id)
                if item_to_edit:
                    st.markdown(f"### ✏️ Editar Joya: **{item_to_edit['name']}** (ID: {item_to_edit['id']})")
                    
                    with st.form("edit_product_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("Nombre de la Joya*", value=item_to_edit['name'])
                            edit_price = st.number_input("Precio (Bs.)*", min_value=0.0, value=float(item_to_edit['price']), step=10.0, format="%.2f")
                            edit_description = st.text_area("Descripción detallada", value=item_to_edit['description'] or "", height=120)
                            
                        with col2:
                            # Categorías de edición
                            st.write("Categoría (selecciona una o más)*")
                            edit_cat_cols = st.columns(3)
                            current_cats = [c.strip() for c in (item_to_edit['category'] or '').split(',')]
                            selected_edit_cats = []
                            for i, cat in enumerate(CATEGORIES):
                                with edit_cat_cols[i % 3]:
                                    is_checked = cat in current_cats
                                    if st.checkbox(cat, value=is_checked, key=f"cat_edit_{cat}"):
                                        selected_edit_cats.append(cat)
                                        
                            # Materiales de edición
                            st.write("Material (selecciona uno o más)*")
                            edit_mat_cols = st.columns(3)
                            current_mats = [m.strip() for m in (item_to_edit['material'] or '').split(',')]
                            selected_edit_mats = []
                            for i, mat in enumerate(MATERIALS):
                                with edit_mat_cols[i % 3]:
                                    is_checked = mat in current_mats
                                    if st.checkbox(mat, value=is_checked, key=f"mat_edit_{mat}"):
                                        selected_edit_mats.append(mat)
                                        
                            # Imagen de edición (soporta Base64 y local)
                            if item_to_edit['image_path']:
                                if item_to_edit['image_path'].startswith("data:image") or os.path.exists(item_to_edit['image_path']):
                                    st.image(item_to_edit['image_path'], width=150, caption="Imagen actual")
                            
                            edit_uploaded_image = st.file_uploader("Subir nueva imagen (reemplazará la actual)", type=["jpg", "jpeg", "png"])
                            delete_image = st.checkbox("Eliminar imagen actual (dejar la joya sin foto)", key="edit_delete_image_chk")
                            
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            save_btn = st.form_submit_button("Guardar Cambios")
                        with col_btn2:
                            cancel_btn = st.form_submit_button("Cancelar")
                            
                        if save_btn:
                            if not edit_name:
                                st.error("El nombre es requerido.")
                            elif edit_price <= 0:
                                st.error("El precio debe ser mayor a 0.")
                            elif not selected_edit_cats:
                                st.error("Debes seleccionar al menos una categoría.")
                            elif not selected_edit_mats:
                                st.error("Debes seleccionar al menos un material.")
                            else:
                                new_image_path = item_to_edit['image_path']
                                
                                if delete_image:
                                    new_image_path = ""
                                elif edit_uploaded_image is not None:
                                    new_image_path = encode_image_to_base64(edit_uploaded_image)
                                        
                                # Actualizar en base de datos
                                database.update_item(
                                    item_id=item_to_edit['id'],
                                    name=edit_name,
                                    category=", ".join(selected_edit_cats),
                                    material=", ".join(selected_edit_mats),
                                    price=edit_price,
                                    description=edit_description,
                                    image_path=new_image_path
                                )
                                st.success("¡Los cambios se han guardado!")
                                st.session_state.edit_item_id = None
                                st.rerun()
                                
                        if cancel_btn:
                            st.session_state.edit_item_id = None
                            st.rerun()
                            
                st.markdown("---")

            # Tabla del inventario
            st.write("Joyas Registradas:")
            
            # Encabezados de tabla
            t_col_id, t_col_img, t_col_name, t_col_cat, t_col_mat, t_col_price, t_col_actions = st.columns([0.8, 1.2, 2.5, 2.5, 2.5, 1.5, 2.0])
            
            with t_col_id:
                st.markdown('<div class="notranslate" style="font-weight: bold; color: #1A2B4C;">🆔 ID</div>', unsafe_allow_html=True)
            with t_col_img:
                st.markdown('<div style="font-weight: bold; color: #1A2B4C;">🖼️ Imagen</div>', unsafe_allow_html=True)
            with t_col_name:
                st.markdown('<div style="font-weight: bold; color: #1A2B4C;">📝 Nombre</div>', unsafe_allow_html=True)
            with t_col_cat:
                st.markdown('<div style="font-weight: bold; color: #1A2B4C;">🏷️ Categorías</div>', unsafe_allow_html=True)
            with t_col_mat:
                st.markdown('<div style="font-weight: bold; color: #1A2B4C;">🛠️ Materiales</div>', unsafe_allow_html=True)
            with t_col_price:
                st.markdown('<div style="font-weight: bold; color: #1A2B4C;">💰 Precio</div>', unsafe_allow_html=True)
            with t_col_actions:
                st.markdown('<div style="font-weight: bold; color: #1A2B4C;">⚙️ Acciones</div>', unsafe_allow_html=True)
                
            st.markdown("<hr style='margin: 5px 0 10px 0; border-top: 2px solid #E2E8F0;'>", unsafe_allow_html=True)
            
            for item in all_items:
                r_col_id, r_col_img, r_col_name, r_col_cat, r_col_mat, r_col_price, r_col_actions = st.columns([0.8, 1.2, 2.5, 2.5, 2.5, 1.5, 2.0])
                
                with r_col_id:
                    st.markdown(f'<div class="notranslate" style="background-color: #E2E8F0; color: #1A2B4C; padding: 4px 8px; border-radius: 6px; text-align: center; font-weight: bold; width: fit-content; margin-top: 10px;">{item["id"]}</div>', unsafe_allow_html=True)
                with r_col_img:
                    if item['image_path']:
                        if item['image_path'].startswith("data:image") or os.path.exists(item['image_path']):
                            st.image(item['image_path'], width=65)
                        else:
                            st.markdown('<div style="color: #64748B; font-style: italic; margin-top: 10px;">Sin foto</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color: #64748B; font-style: italic; margin-top: 10px;">Sin foto</div>', unsafe_allow_html=True)
                with r_col_name:
                    st.markdown(f'<div style="font-weight: 600; color: #1A2B4C; margin-top: 10px;">{item["name"]}</div>', unsafe_allow_html=True)
                with r_col_cat:
                    # Mostrar las categorías con sus iconos
                    cats_styled = ", ".join([get_cat_with_icon(c) for c in (item['category'] or '').split(',') if c.strip()])
                    st.markdown(f'<div style="font-size: 0.9rem; margin-top: 10px;">{cats_styled}</div>', unsafe_allow_html=True)
                with r_col_mat:
                    # Mostrar los materiales con sus iconos
                    mats_styled = ", ".join([get_mat_with_icon(m) for m in (item['material'] or '').split(',') if m.strip()])
                    st.markdown(f'<div style="font-size: 0.9rem; margin-top: 10px;">{mats_styled}</div>', unsafe_allow_html=True)
                with r_col_price:
                    st.markdown(f'<div style="color: #27AE60; font-weight: bold; font-size: 1.1rem; margin-top: 10px;">Bs. {item["price"]:,.2f}</div>', unsafe_allow_html=True)
                with r_col_actions:
                    # Botones de editar y eliminar
                    col_btn_edit, col_btn_del = st.columns(2)
                    with col_btn_edit:
                        if st.button("✏️", key=f"edit_btn_{item['id']}"):
                            st.session_state.edit_item_id = item['id']
                            st.rerun()
                    with col_btn_del:
                        if st.button("🗑️", key=f"del_btn_{item['id']}"):
                            database.delete_item(item['id'])
                            st.success(f"Joya ID {item['id']} eliminada.")
                            st.rerun()
                st.markdown("<hr style='margin: 8px 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)

# --- CONTENIDO: MI CARRITO ---
if st.session_state.active_tab == "🛒 Mi Carrito":
    st.subheader("🛒 Tu Carrito de Compras")
    
    if not st.session_state.cart:
        st.info("Tu Carrito está vacío. Explora el catálogo y agrega hermosas joyas para comenzar.")
    else:
        # Detalle de productos
        total_price = 0.0
        cart_items_data = []
        
        for item_id, qty in list(st.session_state.cart.items()):
            item = database.get_item(item_id)
            if item:
                subtotal = item['price'] * qty
                total_price += subtotal
                cart_items_data.append((item, qty, subtotal))
        
        st.markdown("### Artículos en el Carrito")
        for item, qty, subtotal in cart_items_data:
            c_img, c_det, c_prc, c_actions = st.columns([1, 3, 2, 2])
            with c_img:
                if item['image_path']:
                    st.image(item['image_path'], width=70)
                else:
                    st.markdown("<div style='background-color:#E2E8F0; width:70px; height:70px; border-radius:4px; display:flex; align-items:center; justify-content:center;'><span style='font-size:10px; color:#64748B;'>Sin foto</span></div>", unsafe_allow_html=True)
            with c_det:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"<span style='font-size:0.8rem; color:#7F8C8D;'>{item['category']} | {item['material']}</span>", unsafe_allow_html=True)
            with c_prc:
                st.markdown(f"Bs. {item['price']:,.2f} x {qty}")
                st.markdown(f"**Subtotal: Bs. {subtotal:,.2f}**")
            with c_actions:
                col_btn_m, col_btn_p, col_btn_r = st.columns(3)
                with col_btn_m:
                    if st.button("➖", key=f"cart_page_minus_{item['id']}"):
                        if st.session_state.cart[item['id']] > 1:
                            st.session_state.cart[item['id']] -= 1
                        else:
                            del st.session_state.cart[item['id']]
                        st.rerun()
                with col_btn_p:
                    if st.button("➕", key=f"cart_page_plus_{item['id']}"):
                        st.session_state.cart[item['id']] += 1
                        st.rerun()
                with col_btn_r:
                    if st.button("🗑️", key=f"cart_page_remove_{item['id']}"):
                        del st.session_state.cart[item['id']]
                        st.rerun()
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            
        st.markdown(f"<h3 style='text-align: right; color: #1A2B4C; margin-bottom:20px;'>Total del Pedido: Bs. {total_price:,.2f}</h3>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📋 Datos para la Entrega y Confirmación")
        
        with st.form("checkout_form"):
            name = st.text_input("Nombre Completo del Comprador*", placeholder="Ej. Juan Pérez")
            phone = st.text_input("Celular de Contacto*", placeholder="Ej. 72825322")
            address = st.text_area("Dirección de Entrega y Referencias*", placeholder="Ej. Av. América y Santa Cruz, edificio Las Torres, Depto 4B, frente al banco.")
            gps_link = st.text_input("Enlace de ubicación GPS (opcional, copia y pega abajo)", placeholder="https://www.google.com/maps?q=...")
            
            st.write("📍 **Obtener Ubicación GPS Exacta (Opcional):**")
            # Inyección de Geolocation en HTML
            components.html("""
            <div style="font-family: sans-serif; display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                <button type="button" onclick="getLocation()" style="background-color: #1A2B4C; color: #D4AF37; border: 1px solid #D4AF37; border-radius: 4px; padding: 8px 12px; cursor: pointer; font-size: 13px; font-weight: bold; transition: all 0.3s ease;">
                    📍 Copiar mi Ubicación GPS al Portapapeles
                </button>
                <span id="geo-status" style="font-size: 12px; color: #64748B;">Puedes pegarla en el campo de arriba</span>
            </div>
            <script>
            function getLocation() {
                const status = document.getElementById("geo-status");
                if (!navigator.geolocation) {
                    status.textContent = "Geolocalización no soportada por el navegador.";
                    return;
                }
                status.textContent = "Obteniendo coordenadas...";
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const mapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                        // Intentar copiar al portapapeles
                        navigator.clipboard.writeText(mapsUrl).catch(err => console.log("Error al copiar:", err));
                        
                        // Intentar pegar directamente en el campo de texto del padre
                        try {
                            const parentDoc = window.parent.document;
                            const inputs = parentDoc.getElementsByTagName('input');
                            let target = null;
                            for (let i = 0; i < inputs.length; i++) {
                                if (inputs[i].placeholder && inputs[i].placeholder.indexOf("https://www.google.com/maps") !== -1) {
                                    target = inputs[i];
                                    break;
                                }
                            }
                            if (target) {
                                target.value = mapsUrl;
                                target.dispatchEvent(new Event('input', { bubbles: true }));
                                target.dispatchEvent(new Event('change', { bubbles: true }));
                                status.innerHTML = "✅ <b>¡Ubicación detectada y pegada arriba automáticamente!</b>";
                            } else {
                                status.innerHTML = "✅ <b>¡Ubicación copiada!</b> Pégala en el campo de arriba (Ctrl+V).";
                            }
                        } catch (e) {
                            status.innerHTML = "✅ <b>¡Ubicación copiada!</b> Pégala en el campo de arriba (Ctrl+V).";
                        }
                    },
                    (error) => {
                        status.textContent = "Error al obtener ubicación: " + error.message;
                    }
                );
            }
            </script>
            """, height=42)
            
            st.markdown("""
            > 💡 *Nota:* También puedes compartir tu ubicación nativa directamente en el chat de WhatsApp al enviar el pedido.
            """)
            
            agree = st.checkbox("Entiendo que debo realizar el pago por transferencia QR y enviar el comprobante por WhatsApp*")
            
            submit_checkout = st.form_submit_button("Validar Datos y Ver Código QR")
            
            if submit_checkout:
                if not name:
                    st.error("El nombre completo es requerido.")
                elif not phone:
                    st.error("El celular de contacto es requerido.")
                elif not address:
                    st.error("La dirección de entrega es requerida.")
                elif not agree:
                    st.error("Debes confirmar que enviarás el comprobante de pago.")
                else:
                    st.session_state.checkout_data = {
                        "name": name,
                        "phone": phone,
                        "address": address,
                        "gps_link": gps_link,
                        "total": total_price,
                        "items": cart_items_data
                    }
                    st.success("¡Datos validados! Escanea el código QR a continuación para realizar el pago.")
                    st.rerun()
                    
        # Mostrar QR y WhatsApp si ya se guardaron los datos de checkout
        if 'checkout_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 💸 Paso Final: Realizar Pago y Enviar Detalle")
            
            data = st.session_state.checkout_data
            col_qr, col_info = st.columns([1, 1])
            with col_qr:
                qr_base64 = database.get_setting("qr_code")
                if qr_base64:
                    st.image(qr_base64, caption="Código QR de Pago Autorizado", width=280)
                else:
                    st.markdown("""
                        <div style="border: 2px dashed #D4AF37; border-radius: 8px; padding: 40px; text-align: center; background-color: #FAF9F6; max-width:280px;">
                            <span style="font-size: 40px;">📱</span>
                            <p style="color:#1A2B4C; font-weight:bold; margin-top:10px;">QR No Disponible</p>
                            <p style="font-size:12px; color:#7F8C8D;">Por favor, solicita el QR de transferencia al vendedor en el chat de WhatsApp.</p>
                        </div>
                    """, unsafe_allow_html=True)
            with col_info:
                st.markdown(f"""
                **Resumen de la Orden:**
                - **Cliente:** {data['name']}
                - **Celular de Contacto:** {data['phone']}
                - **Total a Transferir:** <span style="font-size:1.3rem; color:#27AE60; font-weight:bold;">Bs. {data['total']:,.2f}</span>
                
                **Instrucciones para finalizar:**
                1. Escanea el código QR de la izquierda y realiza la transferencia bancaria.
                2. Toma una captura de pantalla del comprobante de transferencia exitosa.
                3. Haz clic en el botón verde de abajo **"Confirmar Pedido en WhatsApp"** para abrir el chat con el vendedor.
                4. Envía el mensaje pre-cargado y **adjunta la captura del comprobante y tu ubicación** en el chat.
                """)
                
                # Construir mensaje de WhatsApp
                msg_items = ""
                for item, qty, sub in data['items']:
                    msg_items += f"- {qty}x {item['name']} (Bs. {item['price']:,.2f} c/u)\n"
                
                gps_str = data['gps_link'] if data['gps_link'] else "Se compartirá directamente por el chat de WhatsApp"
                
                raw_message = (
                    f"¡Hola Paola! Quisiera confirmar el siguiente pedido de joyas:\n\n"
                    f"🛒 *DETALLE DEL PEDIDO:*\n{msg_items}\n"
                    f"💰 *TOTAL:* Bs. {data['total']:,.2f}\n\n"
                    f"👤 *CLIENTE:* {data['name']}\n"
                    f"📞 *CONTACTO:* {data['phone']}\n"
                    f"🏠 *DIRECCIÓN:* {data['address']}\n"
                    f"📍 *UBICACIÓN GPS:* {gps_str}\n\n"
                    f"Adjunto la captura del comprobante de pago QR."
                )
                
                encoded_msg = urllib.parse.quote(raw_message)
                wa_phone = database.get_setting("whatsapp_number", "59172825322")
                wa_phone_clean = "".join(filter(str.isdigit, wa_phone))
                
                wa_url = f"https://wa.me/{wa_phone_clean}?text={encoded_msg}"
                
                # Botón de enlace para WhatsApp
                st.markdown(f"""
                    <a href="{wa_url}" target="_blank" class="whatsapp-btn" style="text-align: center; display: block; text-decoration: none; margin-top:20px;">
                        📱 Confirmar Pedido en WhatsApp
                    </a>
                """, unsafe_allow_html=True)
                
                if st.button("Limpiar Carrito y Crear Nuevo Pedido", key="clear_cart_flow"):
                    st.session_state.cart = {}
                    if 'checkout_data' in st.session_state:
                        del st.session_state.checkout_data
                    st.success("Carrito vaciado. ¡Puedes iniciar un nuevo pedido!")
                    st.rerun()

# --- CONTENIDO: CONFIGURACIÓN DE LA TIENDA ---
if st.session_state.is_admin and st.session_state.active_tab == "🔧 Configuración de Tienda":
    if True:
        st.subheader("🔧 Configuración Global de la Tienda")
        
        current_wa = database.get_setting("whatsapp_number", "59172825322")
        current_pwd = database.get_setting("admin_password", "papavi")
        current_qr = database.get_setting("qr_code")
        
        with st.form("store_settings_form"):
            st.markdown("### 📱 Datos de Contacto y Pedidos")
            new_wa = st.text_input("Número de WhatsApp destino*", value=current_wa, help="Ingresar con código de país sin el +, ej: 59172825322")
            
            st.markdown("### 🔒 Seguridad")
            new_pwd = st.text_input("Contraseña del Panel de Administración*", value=current_pwd, type="password")
            confirm_pwd = st.text_input("Confirmar Contraseña Administrador*", value=current_pwd, type="password")

            st.markdown("### 🏷️ Categorías y Materiales de Joyería")
            new_categories = st.text_area("Categorías disponibles (separadas por comas)*", value=categories_setting, help="Ej: Anillo, Collar, Aretes, Pulsera, Dije, Cadena, Otro")
            new_materials = st.text_area("Materiales disponibles (separados por comas)*", value=materials_setting, help="Ej: Oro 18K, Oro Blanco, Plata 925, Baño de Oro, Con Pedrería")
            
            st.markdown("### 💸 Método de Pago QR")
            if current_qr:
                st.image(current_qr, caption="QR de Pago Actual", width=200)
            
            new_qr_file = st.file_uploader("Subir nueva imagen de QR de Pago (reemplazará la actual)", type=["png", "jpg", "jpeg"])
            
            save_config = st.form_submit_button("Guardar Cambios de Configuración")
            
            if save_config:
                if not new_wa:
                    st.error("El número de WhatsApp es requerido.")
                elif not new_pwd:
                    st.error("La contraseña de administrador es requerida.")
                elif new_pwd != confirm_pwd:
                    st.error("Las contraseñas no coinciden.")
                elif not new_categories:
                    st.error("Debes ingresar al menos una categoría.")
                elif not new_materials:
                    st.error("Debes ingresar al menos un material.")
                else:
                    database.set_setting("whatsapp_number", new_wa)
                    database.set_setting("admin_password", new_pwd)
                    database.set_setting("categories", new_categories)
                    database.set_setting("materials", new_materials)
                    
                    if new_qr_file is not None:
                        qr_base_64 = encode_image_to_base64(new_qr_file)
                        database.set_setting("qr_code", qr_base_64)
                        
                    st.success("¡Configuración guardada exitosamente!")
                    st.rerun()

# --- PIE DE PÁGINA (FOOTER) DE LUJO ---
st.markdown("""
    <div class="footer-lux">
        <h4>💎 Joyería Paola España Ribera 💎</h4>
        <p>Exclusividad, Calidad y Elegancia en cada Pieza</p>
        <p style="font-size: 0.85rem; color: #94A3B8; margin-top: 10px;">
            📍 Envíos a todo el país | 💳 Pagos Seguros vía QR | 📱 Soporte por WhatsApp: +591 72825322
        </p>
        <p style="font-size: 0.75rem; color: #64748B; margin-top: 15px; border-top: 1px solid #1E293B; padding-top: 10px;">
            © 2026 Paola España Ribera. Todos los derechos reservados.
        </p>
    </div>
""", unsafe_allow_html=True)
