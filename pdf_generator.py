import os
import base64
from io import BytesIO
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Image
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado para realizar una numeración de páginas en dos pasadas.
    Permite calcular el total de páginas dinámicamente y dibuja encabezados y pies de página.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        # No dibujar encabezado ni pie de página en la portada
        if self._pageNumber == 1:
            return
            
        self.saveState()
        
        # Paleta de colores
        primary_color = colors.HexColor("#1A2B4C") # Azul Marino Profundo
        gray_color = colors.HexColor("#7F8C8D")
        line_color = colors.HexColor("#BDC3C7")
        
        # --- ENCABEZADO ---
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(primary_color)
        self.drawString(54, 755, "PAOLA ESPAÑA RIBERA")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(gray_color)
        self.drawRightString(558, 755, "Catálogo de Joyas Exclusivas")
        
        # Línea divisoria del encabezado
        self.setStrokeColor(line_color)
        self.setLineWidth(0.5)
        self.line(54, 747, 558, 747)
        
        # --- PIE DE PÁGINA ---
        # Línea divisoria del pie de página
        self.line(54, 52, 558, 52)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(gray_color)
        self.drawString(54, 38, "Contacto Cel: 72825322")
        
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 38, page_text)
        
        self.restoreState()

def create_image_flowable(image_data, max_width, max_height):
    """
    Carga una imagen (ya sea ruta de archivo local o cadena Base64) 
    y retorna un objeto Flowable de ReportLab escalado proporcionalmente.
    Si la imagen no existe o falla, retorna un bloque de texto que sirve como marcador de posición.
    """
    if not image_data:
        return create_placeholder_flowable(max_width, max_height, "Sin Imagen")
        
    try:
        # Caso 1: La imagen es una cadena Base64
        if isinstance(image_data, str) and image_data.startswith("data:image"):
            header, base64_data = image_data.split(",", 1)
            img_bytes = base64.b64decode(base64_data)
            img_buf = BytesIO(img_bytes)
            
            with PILImage.open(img_buf) as img:
                img_w, img_h = img.size
                
            img_buf.seek(0)
            
            # Calcular proporción de escala
            aspect = img_w / img_h
            if aspect > (max_width / max_height):
                w = max_width
                h = max_width / aspect
            else:
                h = max_height
                w = max_height * aspect
                
            return Image(img_buf, width=w, height=h)
            
        # Caso 2: La imagen es una ruta de archivo local
        elif isinstance(image_data, str) and os.path.exists(image_data):
            with PILImage.open(image_data) as img:
                img_w, img_h = img.size
                
            # Calcular proporción de escala
            aspect = img_w / img_h
            if aspect > (max_width / max_height):
                w = max_width
                h = max_width / aspect
            else:
                h = max_height
                w = max_height * aspect
                
            return Image(image_data, width=w, height=h)
            
        else:
            return create_placeholder_flowable(max_width, max_height, "Sin Imagen")
            
    except Exception as e:
        print(f"Error cargando imagen: {e}")
        return create_placeholder_flowable(max_width, max_height, "Error de Imagen")

def create_placeholder_flowable(width, height, text):
    """Crea una celda de tabla como marcador de posición cuando no hay imagen disponible."""
    style = ParagraphStyle(
        'PlaceholderStyle',
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=colors.HexColor('#95A5A6'),
        alignment=1 # Centrado
    )
    p = Paragraph(text, style)
    t = Table([[p]], colWidths=[width], rowHeights=[height])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECF0F1')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
    ]))
    return t

def generate_catalog_pdf(items, output_filename="catalog.pdf", catalog_title="Catálogo de Joyas"):
    """
    Genera un archivo PDF con la portada y el catálogo de joyas.
    """
    # Configuración de documento
    # Márgenes de 54 pt (0.75 pulgadas) arriba/abajo y lados.
    # Ajustamos margen superior e inferior a 72 pt para dejar espacio a encabezado/pie.
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    # Hojas de estilo
    styles = getSampleStyleSheet()
    
    # Colores
    c_primary = colors.HexColor("#1A2B4C")  # Azul Marino Profundo
    c_secondary = colors.HexColor("#D4AF37") # Oro
    c_dark = colors.HexColor("#2C3E50")      # Gris Oscuro
    c_price = colors.HexColor("#27AE60")     # Verde Esmeralda para Precios
    c_muted = colors.HexColor("#7F8C8D")     # Gris Mudo
    
    # Nuevos estilos personalizados
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        textColor=c_primary,
        alignment=1, # Centrado
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=18,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=40
    )
    
    info_style = ParagraphStyle(
        'CoverInfo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=c_dark,
        alignment=1,
        leading=18
    )
    
    prod_name_style = ParagraphStyle(
        'ProductName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=c_primary,
        spaceAfter=4,
        leading=14
    )
    
    prod_price_style = ParagraphStyle(
        'ProductPrice',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=c_price,
        spaceAfter=4
    )
    
    prod_meta_style = ParagraphStyle(
        'ProductMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=c_secondary,
        spaceAfter=4
    )
    
    prod_desc_style = ParagraphStyle(
        'ProductDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=c_dark,
        leading=11
    )

    story = []
    
    # ==========================================
    # PORTADA (PÁGINA 1)
    # ==========================================
    story.append(Spacer(1, 150))
    story.append(Paragraph(catalog_title.upper(), title_style))
    
    # Línea decorativa
    line_table = Table([['']], colWidths=[200], rowHeights=[3])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Colección Exclusiva", subtitle_style))
    story.append(Spacer(1, 100))
    
    contact_html = f"""
    <b>Presentado por:</b><br/>
    <font size="14" color="{c_primary.hexval()}"><b>Paola España Ribera</b></font><br/>
    Celular: 72825322<br/>
    Bolivia
    """
    story.append(Paragraph(contact_html, info_style))
    story.append(PageBreak())
    
    # ==========================================
    # CUADRÍCULA DE PRODUCTOS (PÁGINAS POSTERIORES)
    # ==========================================
    # Organizamos los productos en una cuadrícula de 2 columnas.
    # Ancho imprimible = 492 pt para encajar con el frame predeterminado
    # Definimos columnas: 230 pt (Prod 1), 32 pt (Espacio), 230 pt (Prod 2)
    col_width = 230
    spacer_width = 32
    
    grid_data = []
    current_row = []
    
    for item in items:
        # Construir el bloque para este producto
        prod_elements = []
        
        # Imagen
        img_flowable = create_image_flowable(item.get('image_path'), max_width=220, max_height=150)
        prod_elements.append(img_flowable)
        prod_elements.append(Spacer(1, 6))
        
        # Nombre
        prod_elements.append(Paragraph(item.get('name', 'Sin Nombre'), prod_name_style))
        
        # Categoría y Material
        cat = item.get('category', '')
        mat = item.get('material', '')
        meta_parts = []
        if cat:
            meta_parts.append(cat)
        if mat:
            meta_parts.append(mat)
        meta_str = " | ".join(meta_parts)
        if meta_str:
            prod_elements.append(Paragraph(meta_str, prod_meta_style))
            
        # Precio
        price_val = item.get('price', 0.0)
        prod_elements.append(Paragraph(f"Bs. {price_val:,.2f}", prod_price_style))
        
        # Descripción
        desc = item.get('description', '')
        if desc:
            # Limitar descripción larga si es necesario para evitar desbordes excesivos
            if len(desc) > 120:
                desc = desc[:117] + "..."
            prod_elements.append(Paragraph(desc, prod_desc_style))
            
        # Agregamos los elementos directamente (la celda de la tabla los mantendrá juntos)
        current_row.append(prod_elements)
        
        # Si completamos la fila (2 productos)
        if len(current_row) == 2:
            grid_data.append([current_row[0], "", current_row[1]])
            current_row = []
            
    # Si queda un producto huérfano al final
    if len(current_row) == 1:
        grid_data.append([current_row[0], "", ""])
        
    if grid_data:
        # Crear la tabla de la cuadrícula
        grid_table = Table(
            grid_data, 
            colWidths=[col_width, spacer_width, col_width]
        )
        
        # Estilos de la tabla para alineación y padding
        # Añadimos un poco de padding vertical entre filas para que se vea aireado
        t_style = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 25), 
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ])
        grid_table.setStyle(t_style)
        story.append(grid_table)
    else:
        # Mensaje si no hay productos
        no_items_style = ParagraphStyle(
            'NoItems',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=12,
            textColor=c_muted,
            alignment=1,
            spaceBefore=50
        )
        story.append(Paragraph("No hay joyas disponibles en el catálogo en este momento.", no_items_style))
        
    # Construir el documento usando el Canvas personalizado NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
