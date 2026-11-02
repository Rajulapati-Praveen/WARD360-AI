from io import BytesIO

from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _chart(points, color, title):
    d = Drawing(440, 130)
    if len(points) >= 2:
        lp = LinePlot()
        lp.x, lp.y, lp.width, lp.height = 40, 20, 380, 90
        lp.data = [points]
        lp.lines[0].strokeColor = color
        lp.lines[0].strokeWidth = 1.2
        lp.xValueAxis.labels.fontSize = 7
        lp.yValueAxis.labels.fontSize = 7
        d.add(lp)
    return [Paragraph(title, getSampleStyleSheet()["Heading4"]), d]


def build_pdf(r: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
    st = getSampleStyleSheet()
    navy = colors.HexColor("#0b1f44")
    el = [Paragraph(f"WARD360 AI - {r['period'].capitalize()} Health Summary", st["Title"]),
          Paragraph(f"Patient: {r['patient']['name']} (age {r['patient']['age']}) &nbsp; | &nbsp; Generated: {r['generated_at']}", st["Normal"]),
          Paragraph("<b>SYNTHETIC / SIMULATED DATA.</b> Decision-support summary only. Not a medical record and not a diagnosis.", st["Normal"]),
          Spacer(1, 8)]

    def table(rows, widths=None):
        t = Table(rows, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), navy), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                               ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        return t

    el.append(Paragraph("Measurement summary", st["Heading3"]))
    rows = [["Measurement", "Min", "Mean", "Max", "Readings"]]
    for k, s in r["stats"].items():
        rows.append([r["labels"][k], s["min"], s["mean"], s["max"], s["count"]])
    el.append(table(rows))
    el.append(Spacer(1, 6))
    a = r["availability"]
    el.append(Paragraph(f"Sensor availability: {a['good_pct']}% good-quality readings "
                        f"({a['total']} total, {a['poor']} poor, {a['missing']} missing).", st["Normal"]))
    el.append(Paragraph(f"Risk observations: " + ", ".join(f"{k}: {v}" for k, v in r["risk_counts"].items()), st["Normal"]))
    for key, color, title in (("heart_rate", colors.HexColor("#dc2626"), "Heart rate (bpm)"), ("spo2", colors.HexColor("#2563eb"), "SpO2 (%)")):
        el += _chart(r["chart"].get(key, []), color, title)
    el.append(Paragraph(f"Anomaly observations ({r['anomaly_count']})", st["Heading3"]))
    rows = [["Time", "Measurement", "Explanation"]] + [[x["ts"][:19], x["feature"], Paragraph(x["explanation"], st["BodyText"])] for x in r["anomalies"][:15]]
    el.append(table(rows, [90, 80, 300]) if len(rows) > 1 else Paragraph("None recorded.", st["Normal"]))
    el.append(Paragraph(f"Alerts ({r['alert_count']}) and acknowledgement history", st["Heading3"]))
    rows = [["Time", "Level", "Source", "Status", "Acknowledged by"]]
    for x in r["alerts"][:25]:
        ack = "; ".join(f"{k['by']} @ {k['ts'][11:19]}" for k in x["acknowledgements"]) or "-"
        rows.append([x["created_at"][:19], x["level"], x["source"], x["status"], Paragraph(ack, st["BodyText"])])
    el.append(table(rows, [90, 55, 55, 70, 200]) if len(rows) > 1 else Paragraph("None recorded.", st["Normal"]))
    el += [Spacer(1, 10), Paragraph("Limitations: simulated data; personal-baseline statistics and an Isolation Forest are used for "
                                    "unusual-pattern detection. Forecasts are experimental. Always consult a qualified healthcare professional.", st["Italic"])]
    doc.build(el)
    return buf.getvalue()
