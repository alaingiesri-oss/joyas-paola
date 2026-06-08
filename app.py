import streamlit as st
import os
import uuid
import base64
from io import BytesIO
from PIL import Image as PILImage
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

# Configuración de página con título e ícono
st.set_page_config(
    page_title="Gestor de Joyas - Paola España Ribera",
    page_icon="💎",
    layout="wide"
)

# Inicializar Base de Datos y Carpeta de Cargas
database.init_db()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    
    /* Tarjetas de productos en la galería */
    .product-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #D4AF37;
    }
    
    /* Etiquetas de categoría y material */
    .badge-cat {
        background-color: #EBF8FF;
        color: #2B6CB0;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
        display: inline-block;
    }
    
    .badge-mat {
        background-color: #FEFCBF;
        color: #B7791F;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
        display: inline-block;
    }
    
    .price-text {
        font-size: 1.25rem;
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
    </style>
""", unsafe_allow_html=True)

# --- LISTAS DE SELECCIÓN (CASILLAS DE VERIFICACIÓN) ---
CATEGORIES = ["Anillo", "Collar", "Aretes", "Pulsera", "Dije", "Cadena", "Gargantilla", "Esclava", "Otro"]
MATERIALS = ["Oro 18K", "Oro 24K", "Oro Blanco", "Oro Rosa", "Plata 925", "Plata Ley", "Platino", "Acero Inoxidable", "Baño de Oro", "Con Pedrería"]

# Banner de Encabezado Principal
st.markdown("""
    <div class="header-banner">
        <h1>Joyas Paola España Ribera</h1>
        <p>Catálogo Digital y Gestión de Inventario Exclusivo</p>
    </div>
""", unsafe_allow_html=True)

# Inicializar estados de la aplicación
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = {}
if 'edit_item_id' not in st.session_state:
    st.session_state.edit_item_id = None

# Pestañas principales
tab_gallery, tab_add, tab_manage = st.tabs([
    "🛍️ Catálogo y PDF", 
    "➕ Agregar Nueva Joya", 
    "⚙️ Gestionar Inventario"
])

# --- CONTENIDO: AGREGAR NUEVA JOYA ---
with tab_add:
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
with tab_gallery:
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
        
    st.subheader(f"Catálogo de Joyas ({len(filtered_items)} mostradas)")
    
    # Acciones masivas de selección para el catálogo
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
    items_to_include = [item for item in filtered_items if st.session_state.selected_items.get(item['id'], True)]
    
    st.sidebar.write(f"Joyas seleccionadas para el PDF: {len(items_to_include)}")
    
    if len(items_to_include) > 0:
        pdf_btn = st.sidebar.button("Generar PDF")
        if pdf_btn:
            pdf_filename = "catalogo_joyas.pdf"
            try:
                pdf_generator.generate_catalog_pdf(
                    items_to_include, 
                    output_filename=pdf_filename, 
                    catalog_title=catalog_pdf_title
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
                
                badges_cat_html = "".join([f'<span class="badge-cat">{c}</span>' for c in cats if c])
                badges_mat_html = "".join([f'<span class="badge-mat">{m}</span>' for m in mats if m])
                
                st.markdown(f"<div>{badges_cat_html}{badges_mat_html}</div>", unsafe_allow_html=True)
                
                if item['description']:
                    st.markdown(f"<p style='color:#475569; font-size:0.9rem; margin-top:8px;'>{item['description']}</p>", unsafe_allow_html=True)
                
                # Checkbox para incluir en el catálogo PDF
                st.session_state.selected_items[item['id']] = st.checkbox(
                    "Incluir en catálogo PDF", 
                    value=st.session_state.selected_items[item['id']], 
                    key=f"check_include_{item['id']}"
                )
                st.write("")

# --- CONTENIDO: GESTIONAR INVENTARIO (TABLA Y EDICIÓN/ELIMINACIÓN) ---
with tab_manage:
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
                            
                            # Si se subió una nueva imagen, codificar a Base64 y borrar la anterior si era archivo local
                            if edit_uploaded_image is not None:
                                if new_image_path and not new_image_path.startswith("data:image") and os.path.exists(new_image_path):
                                    try:
                                        os.remove(new_image_path)
                                    except Exception:
                                        pass
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
        t_col_id, t_col_img, t_col_name, t_col_cat, t_col_mat, t_col_price, t_col_actions = st.columns([0.5, 1, 2, 2, 2, 1, 1.5])
        
        with t_col_id:
            st.markdown("**ID**")
        with t_col_img:
            st.markdown("**Imagen**")
        with t_col_name:
            st.markdown("**Nombre**")
        with t_col_cat:
            st.markdown("**Categorías**")
        with t_col_mat:
            st.markdown("**Materiales**")
        with t_col_price:
            st.markdown("**Precio**")
        with t_col_actions:
            st.markdown("**Acciones**")
            
        st.markdown("<hr style='margin: 5px 0 10px 0;'>", unsafe_allow_html=True)
        
        for item in all_items:
            r_col_id, r_col_img, r_col_name, r_col_cat, r_col_mat, r_col_price, r_col_actions = st.columns([0.5, 1, 2, 2, 2, 1, 1.5])
            
            with r_col_id:
                st.write(item['id'])
            with r_col_img:
                if item['image_path']:
                    if item['image_path'].startswith("data:image") or os.path.exists(item['image_path']):
                        st.image(item['image_path'], width=50)
                    else:
                        st.write("Sin foto")
                else:
                    st.write("Sin foto")
            with r_col_name:
                st.write(item['name'])
            with r_col_cat:
                st.write(item['category'])
            with r_col_mat:
                st.write(item['material'])
            with r_col_price:
                st.write(f"Bs. {item['price']:,.2f}")
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
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
