import io
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)
from reportlab.lib.units import inch

from src.analyzer import detect_anomalies
from src.household_manager import mask_consumer_name, mask_connection_no


def plot_trend_to_buffer(analysis: dict) -> io.BytesIO:
    """Generates an in-memory high-res PNG chart for the specific household."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    short_months = analysis.get('short_months', [])
    units = analysis.get('units', [])

    fig, ax = plt.subplots(figsize=(7.5, 3.2), dpi=180)
    plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9})

    if len(units) > 1:
        x_idx = list(range(len(units)))
        ax.plot(x_idx, units, marker='o', markersize=7, color='#1565C0', linewidth=2.5,
                markerfacecolor='#FFFFFF', markeredgewidth=2)
        ax.fill_between(x_idx, units, alpha=0.12, color='#1565C0')
        ax.set_xticks(x_idx)
        ax.set_xticklabels(short_months)
    else:
        ax.bar(short_months, units, color='#1565C0', width=0.35, edgecolor='#0D47A1')

    for i, u in enumerate(units):
        ax.annotate(f"{u} kWh", (i, u), textcoords="offset points", xytext=(0, 8),
                    ha='center', fontweight='bold', color='#0D47A1', fontsize=8.5)

    ax.set_title("Household Electricity Consumption Progression", fontsize=11, fontweight='bold', color='#0D47A1', pad=10)
    ax.set_ylabel("Units (kWh)", fontsize=9, fontweight='semibold')
    ax.set_ylim(0, max(units) * 1.25 if units else 100)
    ax.grid(axis='y', linestyle='--', alpha=0.45)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf_report(df: pd.DataFrame, analysis: dict, consumer_info: dict = None) -> bytes:
    """
    Generates a publication-grade PDF report of WattWise Energy Consumption Analysis
    dynamically tailored for ANY household.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0D47A1'),
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#546E7A')
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1565C0'),
        spaceAfter=5,
        spaceBefore=10
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#263238')
    )
    
    disclaimer_style = ParagraphStyle(
        'Disclaimer_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#C62828')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#263238'),
        alignment=1
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("⚡ WattWise – Household Energy Intelligence", title_style))
    story.append(Paragraph("Tamil Nadu TANGEDCO/TNPDCL Domestic Electricity Consumption Audit", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1565C0'), spaceAfter=8))

    # Consumer Metadata
    raw_name = consumer_info.get('consumer_name') if consumer_info else df.get('consumer_name', [None])[0] or "Household Consumer"
    raw_conn = consumer_info.get('connection_no') if consumer_info else df.get('connection_no', [None])[0] or "N/A"
    section = consumer_info.get('section') if consumer_info else df.get('section', [None])[0] or "Domestic Section"
    tariff = consumer_info.get('tariff_category') if consumer_info else df.get('tariff_category', [None])[0] or "LT Domestic"
    is_demo = consumer_info.get('is_demo', False) if consumer_info else False

    disp_name = raw_name if is_demo else mask_consumer_name(raw_name)
    disp_conn = raw_conn if is_demo else mask_connection_no(raw_conn)

    meta_data = [
        [
            Paragraph(f"<b>Household / Consumer:</b> {disp_name}", body_style),
            Paragraph(f"<b>Service Connection:</b> {disp_conn}", body_style)
        ],
        [
            Paragraph(f"<b>Section / Region:</b> {section}", body_style),
            Paragraph(f"<b>Tariff Category:</b> {tariff}", body_style)
        ],
        [
            Paragraph(f"<b>Audit Date:</b> {datetime.now().strftime('%d %B %Y')}", body_style),
            Paragraph(f"<b>Billing Cycles Analyzed:</b> {len(df)} cycle{'s' if len(df)>1 else ''}", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5F7FA')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CFD8DC')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ECEFF1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 2. Key Performance Indicators (KPIs)
    story.append(Paragraph("1. Executive Summary & Household Metrics", h1_style))
    
    total_units = analysis.get('total_units', 0)
    total_amt = analysis.get('total_amount', 0.0)
    avg_units = analysis.get('avg_units', 0.0)
    avg_amt = analysis.get('avg_amount', 0.0)
    max_month = analysis.get('max_units_month', 'N/A')
    max_units = analysis.get('max_units', 0)
    min_month = analysis.get('min_units_month', 'N/A')
    min_units = analysis.get('min_units', 0)

    kpi_data = [
        [
            Paragraph(f"<b>Total Consumption</b><br/><font size='11' color='#0D47A1'><b>{total_units:,} kWh</b></font>", body_style),
            Paragraph(f"<b>Total Billed</b><br/><font size='11' color='#00695C'><b>₹{total_amt:,.2f}</b></font>", body_style),
            Paragraph(f"<b>Average / Cycle</b><br/><font size='11' color='#1565C0'><b>{avg_units:.1f} kWh</b> (₹{avg_amt:,.0f})</font>", body_style),
            Paragraph(f"<b>Peak Period</b><br/><font size='11' color='#C62828'><b>{max_units} kWh</b> ({max_month})</font>", body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E8EAF6')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#9FA8DA')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#C5CAE9')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 8))

    # 3. Cycle Breakdown Table
    story.append(Paragraph("2. Billing Cycle History & Consumption Progression", h1_style))
    
    headers = ["Cycle Month", "Bill Date", "Meter Reading", "Units (kWh)", "Net Amount", "Unit Rate", "Quality Note"]
    table_rows = [[Paragraph(h, table_header_style) for h in headers]]
    
    months = analysis.get('months', [])
    units = analysis.get('units', [])
    amounts = analysis.get('amounts', [])
    final_readings = analysis.get('final_readings', [])
    
    for i, m in enumerate(months):
        u = units[i] if i < len(units) else 0
        amt = amounts[i] if i < len(amounts) else 0.0
        mr = f"{final_readings[i]:,.0f}" if i < len(final_readings) and pd.notna(final_readings[i]) else "—"
        rate = f"₹{amt/u:.2f}" if u > 0 else "—"
        
        bdate = "—"
        if 'bill_date' in df.columns and i < len(df):
            val = df['bill_date'].iloc[i]
            if pd.notna(val):
                bdate = val.strftime('%d/%m/%Y') if hasattr(val, 'strftime') else str(val)

        flag = "Verified"
        if 'data_quality_flag' in df.columns and i < len(df):
            raw_flag = str(df['data_quality_flag'].iloc[i])
            flag = "Derived Δ" if "derived" in raw_flag.lower() else ("Confirmed" if "confirmed" in raw_flag.lower() else "OCR Est.")

        table_rows.append([
            Paragraph(m, table_cell_style),
            Paragraph(bdate, table_cell_style),
            Paragraph(mr, table_cell_style),
            Paragraph(f"<b>{u}</b>", table_cell_style),
            Paragraph(f"₹{amt:,.0f}", table_cell_style),
            Paragraph(rate, table_cell_style),
            Paragraph(flag, table_cell_style),
        ])

    cycle_table = Table(table_rows, colWidths=[85, 75, 75, 70, 75, 65, 75])
    cycle_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1565C0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#B0BEC5')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(cycle_table)
    story.append(Spacer(1, 8))

    # 4. Dynamic Embedded Chart (Tailored to this specific household)
    story.append(Paragraph("3. Household Consumption Trajectory Chart", h1_style))
    chart_buffer = plot_trend_to_buffer(analysis)
    img = Image(chart_buffer, width=6.5*inch, height=2.8*inch)
    story.append(img)
    story.append(Spacer(1, 8))

    # 5. Peak Load & Seasonality Insights
    story.append(Paragraph("4. Peak Load & Tariff Anomaly Findings", h1_style))
    spread = max_units - min_units
    anomalies = detect_anomalies(analysis)

    anomaly_text = "• <b>Billing Consistency:</b> No direction mismatch anomalies detected across these billing cycles."
    if anomalies:
        anom_items = []
        for a in anomalies:
            anom_items.append(f"• <b>{a['type'].replace('_', ' ').title()}:</b> {a['description']}")
        anomaly_text = "<br/>".join(anom_items)

    findings_p1 = (
        f"• <b>Peak Period:</b> Highest recorded consumption for this household was <b>{max_units} kWh</b> in "
        f"<b>{max_month}</b>.<br/>"
        f"• <b>Baseline / Trough Period:</b> Lowest recorded consumption was <b>{min_units} kWh</b> in <b>{min_month}</b>.<br/>"
        f"• <b>Seasonal Variance:</b> Consumption spans a range of <b>{spread} kWh</b> between cycles.<br/>"
        f"{anomaly_text}"
    )
    story.append(Paragraph(findings_p1, body_style))
    story.append(Spacer(1, 6))

    # 6. Experimental Forecast (if >= 2 cycles)
    if len(df) >= 2:
        story.append(Paragraph("5. Experimental Forecast for Next Billing Cycle", h1_style))
        from src.predictor import forecast_next_cycle
        fc = forecast_next_cycle(analysis['units'], analysis['amounts'])
        
        fc_text = (
            f"• <b>Linear Regression Trend (OLS):</b> ~{fc['linear']['predicted_units']} kWh (Est. ₹{fc['estimated_amount_linear']:,.0f})<br/>"
            f"• <b>Moving Average Projection:</b> ~{fc['moving_avg']['predicted_units']} kWh (Est. ₹{fc['estimated_amount_ma']:,.0f})<br/>"
            f"• <b>Planning Target:</b> Focus on keeping bi-monthly consumption below the 500 kWh slab threshold."
        )
        story.append(Paragraph(fc_text, body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            "<b>Scientific Disclaimer:</b> Projections are experimental estimations derived from available billing cycles. "
            "They do not constitute guaranteed utility figures. Intra-day or hourly peaks cannot be inferred from bi-monthly totals.",
            disclaimer_style
        ))
        story.append(Spacer(1, 6))

    # 7. Actionable Recommendations
    story.append(Paragraph("6. Tailored Energy Conservation Plan", h1_style))
    recs_text = (
        "1. <b>AC Thermostat Optimization:</b> Set split air conditioners to 24°C–26°C instead of 18°C–20°C. Each 1°C increase reduces cooling power by ~6%.<br/>"
        "2. <b>Fan-First Cooling Strategy:</b> Utilize ceiling fans (70W) rather than AC (1,200W) during morning and moderate evening hours.<br/>"
        "3. <b>Standby Power Elimination:</b> Switch off unplugged set-top boxes, displays, and chargers to reduce phantom baseline consumption.<br/>"
        "4. <b>Tariff Slab Awareness:</b> TANGEDCO domestic tariffs feature stepped pricing slabs. Keeping usage under 500 kWh avoids higher marginal rates."
    )
    story.append(Paragraph(recs_text, body_style))
    story.append(Spacer(1, 8))

    # Footer rule
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CFD8DC'), spaceAfter=5))
    story.append(Paragraph("WattWise Analytics Engine • Multi-Household Energy Intelligence • Confidential Audit Document", subtitle_style))

    doc.build(story)
    return buffer.getvalue()
