"""
Generación de reportes de ventas en PDF (datos monetarios y de volumen).
"""
from __future__ import annotations

from decimal import Decimal
from io import BytesIO
from itertools import count
from xml.sax.saxutils import escape

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import Category, Pedido, PedidoItem, Product

_CELL_TEXT_INSET_PT = 12
_paragraph_style_id = count()


def _cell_paragraph(
    text,
    col_width_pt: float,
    *,
    font_size: int = 8,
    bold: bool = False,
    align: int = TA_LEFT,
    text_color=colors.black,
) -> Paragraph:
    font_name = "Helvetica-Bold" if bold else "Helvetica"
    raw = str(text if text is not None else "").replace("\r", " ").replace("\n", " ")
    avail = max(20.0, float(col_width_pt) - _CELL_TEXT_INSET_PT)
    lines = simpleSplit(raw, font_name, font_size, avail)
    if not lines:
        lines = [""]
    html = "<br/>".join(escape(line) for line in lines)
    style = ParagraphStyle(
        name=f"WC{next(_paragraph_style_id)}",
        fontName=font_name,
        fontSize=font_size,
        leading=round(font_size * 1.22, 1),
        alignment=align,
        textColor=text_color,
    )
    return Paragraph(html, style)


def _pedidos_considerados():
    return Pedido.objects.exclude(estado="cancelado")


def _compute_stats(category_id: int | None):
    pedidos_qs = _pedidos_considerados()
    items_base = PedidoItem.objects.filter(pedido__in=pedidos_qs)

    if category_id is not None:
        items = items_base.filter(product__category_id=category_id)
        line_total = ExpressionWrapper(
            F("price") * F("quantity"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
        ingresos = items.aggregate(s=Sum(line_total))["s"] or Decimal("0")
        unidades = items.aggregate(s=Sum("quantity"))["s"] or 0
        num_pedidos = items.values("pedido_id").distinct().count()
        cat = Category.objects.filter(pk=category_id).first()
        filtro_txt = cat.name if cat else f"Categoría ID {category_id}"
        ticket_promedio = (ingresos / num_pedidos) if num_pedidos else Decimal("0")
    else:
        ingresos = pedidos_qs.aggregate(s=Sum("total"))["s"] or Decimal("0")
        num_pedidos = pedidos_qs.count()
        unidades = items_base.aggregate(s=Sum("quantity"))["s"] or 0
        filtro_txt = "Todas las categorías"
        ticket_promedio = (ingresos / num_pedidos) if num_pedidos else Decimal("0")

    return {
        "filtro_txt": filtro_txt,
        "total_ingresos": ingresos,
        "total_pedidos": num_pedidos,
        "unidades_vendidas": int(unidades or 0),
        "ticket_promedio": ticket_promedio,
    }


def _breakdown_por_categoria():
    pedidos_qs = _pedidos_considerados()
    items = PedidoItem.objects.filter(pedido__in=pedidos_qs)
    line_total = ExpressionWrapper(
        F("price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    rows = (
        items.values("product__category__name")
        .annotate(ingresos=Sum(line_total), unidades=Sum("quantity"))
        .order_by("-ingresos")
    )
    out = []
    for r in rows:
        nombre = r["product__category__name"] or "Sin categoría"
        ing = r["ingresos"] or Decimal("0")
        u = int(r["unidades"] or 0)
        out.append((nombre, ing, u))
    return out


def _inventory_table_data(category_id: int | None):
    qs = Product.objects.select_related("category").all()
    if category_id is not None:
        qs = qs.filter(category_id=category_id).order_by("name")
    else:
        qs = qs.order_by("category__name", "name")

    rows = []
    total_inventario = Decimal("0")
    for p in qs:
        precio = Decimal(p.price)
        stock = int(p.stock)
        valor = precio * stock
        total_inventario += valor
        cat = p.category.name if p.category else "Sin categoría"
        rows.append(
            {
                "categoria": cat,
                "nombre": p.name,
                "stock": stock,
                "precio": precio,
                "valor": valor,
            }
        )
    return rows, total_inventario


def build_sales_report_pdf_bytes(category_id: int | None) -> bytes:
    stats = _compute_stats(category_id)
    gen_at = timezone.now()
    breakdown = _breakdown_por_categoria() if category_id is None else []
    hdr_white = colors.whitesmoke

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Reporte de ventas ScrewFX",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleCustom",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1a2a3a"),
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    h2 = ParagraphStyle(
        name="H2Custom",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#2c3e50"),
        spaceBefore=10,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    body = ParagraphStyle(
        name="BodyCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
    )

    story = []
    story.append(Paragraph("ScrewFX — Reporte de ventas", title_style))
    tz_label = getattr(timezone.get_current_timezone(), "key", None) or str(timezone.get_current_timezone())
    story.append(
        Paragraph(
            f"<b>Fecha de generación:</b> {gen_at.strftime('%d/%m/%Y %H:%M')} ({tz_label})",
            body,
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("<b>Alcance del reporte</b>", h2))
    story.append(
        Paragraph(
            "Se consideran pedidos con cualquier estado excepto <i>cancelado</i>. "
            "Los importes reflejan ventas registradas en el sistema.",
            body,
        )
    )
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        Paragraph(f"<b>Filtro de categoría:</b> {escape(str(stats['filtro_txt']))}", body)
    )
    story.append(Spacer(1, 0.5 * cm))

    ti = stats["total_ingresos"]
    tp = stats["ticket_promedio"]
    w_ind, w_val = 9 * cm, 7 * cm
    data = [
        [
            _cell_paragraph("Indicador", w_ind, font_size=10, bold=True, text_color=hdr_white),
            _cell_paragraph("Valor", w_val, font_size=10, bold=True, align=TA_RIGHT, text_color=hdr_white),
        ],
        [
            _cell_paragraph("Total de pedidos (ventas)", w_ind, font_size=9),
            _cell_paragraph(str(stats["total_pedidos"]), w_val, font_size=9, align=TA_RIGHT),
        ],
        [
            _cell_paragraph("Total de ingresos", w_ind, font_size=9),
            _cell_paragraph(f"${ti:,.2f}", w_val, font_size=9, align=TA_RIGHT),
        ],
        [
            _cell_paragraph("Unidades de producto vendidas", w_ind, font_size=9),
            _cell_paragraph(str(stats["unidades_vendidas"]), w_val, font_size=9, align=TA_RIGHT),
        ],
        [
            _cell_paragraph("Ticket promedio (ingresos / pedidos)", w_ind, font_size=9),
            _cell_paragraph(f"${tp:,.2f}", w_val, font_size=9, align=TA_RIGHT),
        ],
    ]
    t = Table(data, colWidths=[w_ind, w_val])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f8")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cfd8dc")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(t)

    if breakdown:
        story.append(Spacer(1, 0.6 * cm))
        story.append(Paragraph("<b>Desglose de ingresos por categoría</b>", h2))
        bc, bi, bu = 6.5 * cm, 5 * cm, 4.5 * cm
        bd = [
            [
                _cell_paragraph("Categoría", bc, font_size=9, bold=True, text_color=hdr_white),
                _cell_paragraph(
                    "Ingresos (líneas)", bi, font_size=9, bold=True, align=TA_RIGHT, text_color=hdr_white
                ),
                _cell_paragraph("Unidades", bu, font_size=9, bold=True, align=TA_RIGHT, text_color=hdr_white),
            ]
        ]
        for nombre, ing, u in breakdown:
            bd.append(
                [
                    _cell_paragraph(nombre, bc, font_size=8),
                    _cell_paragraph(f"${ing:,.2f}", bi, font_size=8, align=TA_RIGHT),
                    _cell_paragraph(str(u), bu, font_size=8, align=TA_RIGHT),
                ]
            )
        t2 = Table(bd, colWidths=[bc, bi, bu])
        t2.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cfd8dc")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(t2)

    inv_rows, total_inv = _inventory_table_data(category_id)
    story.append(Spacer(1, 0.7 * cm))
    story.append(Paragraph("<b>Inventario del catálogo (existencias actuales)</b>", h2))
    story.append(
        Paragraph(
            "Productos según el filtro del reporte: stock, precio unitario y valor (precio × stock).",
            body,
        )
    )
    story.append(Spacer(1, 0.25 * cm))

    if not inv_rows:
        story.append(Paragraph("<i>No hay productos en este alcance.</i>", body))
    else:
        inv_hdr_white = hdr_white
        if category_id is None:
            c0, c1, c2, c3, c4 = 3.0 * cm, 5.2 * cm, 1.6 * cm, 2.2 * cm, 3.0 * cm
            col_widths = [c0, c1, c2, c3, c4]
            inv_data = [
                [
                    _cell_paragraph("Categoría", c0, font_size=8, bold=True, text_color=inv_hdr_white),
                    _cell_paragraph("Producto", c1, font_size=8, bold=True, text_color=inv_hdr_white),
                    _cell_paragraph("Stock", c2, font_size=8, bold=True, align=TA_RIGHT, text_color=inv_hdr_white),
                    _cell_paragraph("P. unit.", c3, font_size=8, bold=True, align=TA_RIGHT, text_color=inv_hdr_white),
                    _cell_paragraph(
                        "Valor inv.", c4, font_size=8, bold=True, align=TA_RIGHT, text_color=inv_hdr_white
                    ),
                ]
            ]
            for r in inv_rows:
                inv_data.append(
                    [
                        _cell_paragraph(r["categoria"], c0, font_size=7),
                        _cell_paragraph(r["nombre"], c1, font_size=7),
                        _cell_paragraph(str(r["stock"]), c2, font_size=7, align=TA_RIGHT),
                        _cell_paragraph(f"${r['precio']:,.2f}", c3, font_size=7, align=TA_RIGHT),
                        _cell_paragraph(f"${r['valor']:,.2f}", c4, font_size=7, align=TA_RIGHT),
                    ]
                )
            inv_data.append(
                [
                    _cell_paragraph("", c0, font_size=7),
                    _cell_paragraph("", c1, font_size=7),
                    _cell_paragraph("", c2, font_size=7),
                    _cell_paragraph("Total inventario", c3, font_size=8, bold=True, align=TA_RIGHT),
                    _cell_paragraph(f"${total_inv:,.2f}", c4, font_size=8, bold=True, align=TA_RIGHT),
                ]
            )
        else:
            c0, c1, c2, c3 = 7.5 * cm, 1.8 * cm, 2.4 * cm, 3.3 * cm
            col_widths = [c0, c1, c2, c3]
            inv_data = [
                [
                    _cell_paragraph("Producto", c0, font_size=8, bold=True, text_color=inv_hdr_white),
                    _cell_paragraph("Stock", c1, font_size=8, bold=True, align=TA_RIGHT, text_color=inv_hdr_white),
                    _cell_paragraph("P. unit.", c2, font_size=8, bold=True, align=TA_RIGHT, text_color=inv_hdr_white),
                    _cell_paragraph(
                        "Valor inv.", c3, font_size=8, bold=True, align=TA_RIGHT, text_color=inv_hdr_white
                    ),
                ]
            ]
            for r in inv_rows:
                inv_data.append(
                    [
                        _cell_paragraph(r["nombre"], c0, font_size=7),
                        _cell_paragraph(str(r["stock"]), c1, font_size=7, align=TA_RIGHT),
                        _cell_paragraph(f"${r['precio']:,.2f}", c2, font_size=7, align=TA_RIGHT),
                        _cell_paragraph(f"${r['valor']:,.2f}", c3, font_size=7, align=TA_RIGHT),
                    ]
                )
            inv_data.append(
                [
                    _cell_paragraph("", c0, font_size=7),
                    _cell_paragraph("", c1, font_size=7),
                    _cell_paragraph("Total inventario", c2, font_size=8, bold=True, align=TA_RIGHT),
                    _cell_paragraph(f"${total_inv:,.2f}", c3, font_size=8, bold=True, align=TA_RIGHT),
                ]
            )

        inv_table = Table(inv_data, colWidths=col_widths, repeatRows=1)
        last_row = len(inv_data) - 1
        inv_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e5631")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f4faf6")]),
                    ("GRID", (0, 0), (-1, -1), 0.2, colors.HexColor("#b8d4c0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("BACKGROUND", (0, last_row), (-1, last_row), colors.HexColor("#d4edda")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(inv_table)

    story.append(Spacer(1, 0.6 * cm))
    story.append(
        Paragraph(
            "<i>Documento generado automáticamente. Ventas según pedidos; inventario según catálogo al "
            "momento de la generación.</i>",
            body,
        )
    )

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf
